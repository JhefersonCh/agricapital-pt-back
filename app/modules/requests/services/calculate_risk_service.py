from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class RiskLevel(str, Enum):
    VERY_LOW = "MUY_BAJO"
    LOW = "BAJO"
    MEDIUM = "MEDIO"
    HIGH = "ALTO"
    VERY_HIGH = "MUY_ALTO"
    CRITICAL = "CRITICO"


class CreditRequest(BaseModel):
    date_of_birth: date
    annual_income: float = Field(gt=0, json_schema_extra={"description": "Ingreso anual en COP"})
    years_of_agricultural_experience: int = Field(ge=0, le=60)
    has_agricultural_insurance: bool
    internal_credit_history_score: int = Field(ge=0, le=1000)
    current_debt_to_income_ratio: float = Field(ge=0, le=1)
    farm_size_hectares: float = Field(gt=0)
    requested_amount: float = Field(gt=0)
    term_months: int = Field(gt=0, le=360)
    annual_interest_rate: float = Field(gt=0, le=50)
    applicant_contribution_amount: float = Field(ge=0, default=0)
    has_collateral: bool = Field(default=False)
    collateral_value: Optional[float] = Field(default=None, ge=0)
    number_of_dependents: int = Field(ge=0, default=0)
    other_income_sources: float = Field(ge=0, default=0)
    previous_defaults: int = Field(ge=0, default=0)


class RiskAssessmentResult(BaseModel):
    risk_score: float = Field(
        description="Puntaje de riesgo de 0-100 (donde 0 = sin riesgo, 100 = máximo riesgo)"
    )
    risk_level: RiskLevel
    risk_percentage: float = Field(description="Porcentaje de riesgo 0-100%")
    approval_recommendation: bool
    maximum_recommended_amount: float
    recommended_interest_rate: float
    detailed_analysis: dict
    warning_flags: list[str]


class CreditRiskCalculator:
    """
    Calculadora de riesgo crediticio donde:
    - Los puntajes individuales son POSITIVOS (mayor puntaje = menor riesgo)
    - El puntaje final de riesgo es de 0-100 (0 = sin riesgo, 100 = máximo riesgo)
    """

    WEIGHTS = {
        "credit_history": 25,
        "payment_capacity": 20,
        "debt_burden": 15,
        "agricultural_profile": 12,
        "demographics": 8,
        "collateral": 10,
        "loan_characteristics": 10,
    }

    BASE_RATES = {
        RiskLevel.VERY_LOW: 12.0,
        RiskLevel.LOW: 15.0,
        RiskLevel.MEDIUM: 18.0,
        RiskLevel.HIGH: 22.0,
        RiskLevel.VERY_HIGH: 28.0,
        RiskLevel.CRITICAL: 35.0,
    }

    @staticmethod
    def calculate_age(birth_date: date) -> int:
        today = datetime.now().date()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (
            today.month == birth_date.month and today.day < birth_date.day
        ):
            age -= 1
        return age

    @staticmethod
    def calculate_monthly_payment(
        principal: float, annual_rate: float, months: int
    ) -> float:
        if annual_rate <= 0 or months <= 0:
            return 0

        monthly_rate = (annual_rate / 100) / 12
        factor = (1 + monthly_rate) ** months
        return (principal * monthly_rate * factor) / (factor - 1)

    def assess_credit_history(
        self, credit_score: int, previous_defaults: int
    ) -> tuple[float, list[str]]:
        """Retorna puntaje positivo (0-100) donde mayor puntaje = menor riesgo"""
        warnings = []
        score = 0

        # Puntaje de historial crediticio (0-80 puntos)
        if credit_score >= 750:
            score += 80
        elif credit_score >= 700:
            score += 68
        elif credit_score >= 650:
            score += 52
        elif credit_score >= 600:
            score += 36
        elif credit_score >= 550:
            score += 20
            warnings.append("Puntaje crediticio por debajo del promedio")
        else:
            score += 4
            warnings.append("Puntaje crediticio muy bajo - alto riesgo")

        # Puntaje por incumplimientos (0-20 puntos)
        if previous_defaults == 0:
            score += 20
        elif previous_defaults == 1:
            score += 12
            warnings.append("Un incumplimiento previo registrado")
        elif previous_defaults == 2:
            score += 4
            warnings.append("Múltiples incumplimientos previos")
        else:
            score += 0
            warnings.append("Historial de múltiples incumplimientos - riesgo crítico")

        return min(score, 100), warnings

    def assess_payment_capacity(
        self,
        annual_income: float,
        other_income: float,
        monthly_payment: float,
        dependents: int,
    ) -> tuple[float, list[str]]:
        """Retorna puntaje positivo (0-100) donde mayor puntaje = menor riesgo"""
        warnings = []
        score = 0

        total_income = annual_income + other_income
        monthly_income = total_income / 12

        payment_ratio = monthly_payment / monthly_income if monthly_income > 0 else 1

        if payment_ratio <= 0.20:
            score += 60
        elif payment_ratio <= 0.30:
            score += 50
        elif payment_ratio <= 0.40:
            score += 35
        elif payment_ratio <= 0.50:
            score += 20
            warnings.append("Cuota mensual representa un alto porcentaje del ingreso")
        else:
            score += 5
            warnings.append(
                "Cuota mensual excesiva respecto al ingreso - riesgo muy alto"
            )

        monthly_minimum_wages = monthly_income / 1300000

        if monthly_minimum_wages >= 10:
            score += 25
        elif monthly_minimum_wages >= 5:
            score += 20
        elif monthly_minimum_wages >= 3:
            score += 15
        elif monthly_minimum_wages >= 2:
            score += 10
        else:
            score += 5
            warnings.append("Ingresos bajos para el monto solicitado")

        if dependents == 0:
            score += 15
        elif dependents <= 2:
            score += 10
        elif dependents <= 4:
            score += 5
        else:
            score += 0
            warnings.append("Alto número de dependientes reduce capacidad de pago")

        return min(score, 100), warnings

    def assess_debt_burden(
        self, debt_to_income_ratio: float, annual_income: float
    ) -> tuple[float, list[str]]:
        """Retorna puntaje positivo (0-100) donde mayor puntaje = menor riesgo"""
        warnings = []
        if debt_to_income_ratio <= 0.20:
            score = 100
        elif debt_to_income_ratio <= 0.30:
            score = 80
        elif debt_to_income_ratio <= 0.40:
            score = 53
            warnings.append("Nivel de endeudamiento moderadamente alto")
        elif debt_to_income_ratio <= 0.50:
            score = 27
            warnings.append("Alto nivel de endeudamiento existente")
        else:
            score = 7
            warnings.append("Nivel de endeudamiento crítico")

        return score, warnings

    def assess_agricultural_profile(
        self,
        experience_years: int,
        farm_size: float,
        has_insurance: bool,
        annual_income: float,
    ) -> tuple[float, list[str]]:
        """Retorna puntaje positivo (0-100) donde mayor puntaje = menor riesgo"""
        warnings = []
        score = 0

        if experience_years >= 15:
            score += 42
        elif experience_years >= 10:
            score += 33
        elif experience_years >= 5:
            score += 25
        elif experience_years >= 2:
            score += 13
        else:
            score += 4
            warnings.append("Experiencia agrícola limitada aumenta el riesgo")

        income_per_hectare = annual_income / farm_size if farm_size > 0 else 0

        if income_per_hectare >= 5000000:
            score += 33
        elif income_per_hectare >= 3000000:
            score += 25
        elif income_per_hectare >= 2000000:
            score += 17
        elif income_per_hectare >= 1000000:
            score += 8
        else:
            score += 4
            warnings.append("Baja productividad por hectárea")

        if has_insurance:
            score += 25
        else:
            score += 0
            warnings.append(
                "Sin seguro agrícola - mayor exposición a riesgos climáticos"
            )

        return min(score, 100), warnings

    def assess_demographics(self, age: int) -> tuple[float, list[str]]:
        """Retorna puntaje positivo (0-100) donde mayor puntaje = menor riesgo"""
        warnings = []

        if 30 <= age <= 55:
            score = 100
        elif 25 <= age <= 65:
            score = 75
        elif 18 <= age <= 70:
            score = 50
        else:
            score = 25
            if age < 25:
                warnings.append("Edad joven puede indicar falta de experiencia")
            else:
                warnings.append("Edad avanzada puede afectar capacidad de trabajo")

        return score, warnings

    def assess_collateral(
        self, has_collateral: bool, collateral_value: float, requested_amount: float
    ) -> tuple[float, list[str]]:
        """Retorna puntaje positivo (0-100) donde mayor puntaje = menor riesgo"""
        warnings = []

        if not has_collateral or collateral_value == 0:
            score = 0
            warnings.append("Sin garantías reales - mayor riesgo para la entidad")
        else:
            coverage_ratio = (
                collateral_value / requested_amount if requested_amount > 0 else 0
            )
            if coverage_ratio >= 1.5:
                score = 100
            elif coverage_ratio >= 1.2:
                score = 80
            elif coverage_ratio >= 1.0:
                score = 60
            elif coverage_ratio >= 0.8:
                score = 40
                warnings.append(
                    "Garantía insuficiente para cubrir completamente el crédito"
                )
            elif coverage_ratio >= 0.5:
                score = 20
                warnings.append("Garantía baja respecto al monto solicitado")
            else:
                score = 10
                warnings.append("Garantía muy baja respecto al monto solicitado")

        return score, warnings

    def assess_loan_characteristics(
        self,
        requested_amount: float,
        term_months: int,
        annual_income: float,
        contribution: float,
    ) -> tuple[float, list[str]]:
        """Retorna puntaje positivo (0-100) donde mayor puntaje = menor riesgo"""
        warnings = []
        score = 0

        amount_to_income_ratio = (
            requested_amount / annual_income if annual_income > 0 else float("inf")
        )

        if amount_to_income_ratio <= 2:
            score += 50
        elif amount_to_income_ratio <= 3:
            score += 35
        elif amount_to_income_ratio <= 5:
            score += 20
            warnings.append("Monto elevado respecto a ingresos anuales")
        else:
            score += 5
            warnings.append("Monto muy alto respecto a capacidad de ingresos")

        if 12 <= term_months <= 60:
            score += 30
        elif 6 <= term_months <= 120:
            score += 20
        else:
            score += 10
            if term_months < 12:
                warnings.append("Plazo muy corto puede generar cuotas altas")
            else:
                warnings.append("Plazo muy largo aumenta riesgo de incumplimiento")

        contribution_ratio = (
            contribution / requested_amount if requested_amount > 0 else 0
        )

        if contribution_ratio >= 0.30:
            score += 20
        elif contribution_ratio >= 0.20:
            score += 15
        elif contribution_ratio >= 0.10:
            score += 10
        else:
            score += 0
            warnings.append("Bajo aporte propio aumenta el riesgo")

        return min(score, 100), warnings

    def calculate_risk_score(self, request: CreditRequest) -> RiskAssessmentResult:
        age = self.calculate_age(request.date_of_birth)
        monthly_payment = self.calculate_monthly_payment(
            request.requested_amount, request.annual_interest_rate, request.term_months
        )

        all_warnings = []
        detailed_scores = {}

        credit_score, credit_warnings = self.assess_credit_history(
            request.internal_credit_history_score, request.previous_defaults
        )

        all_warnings.extend(credit_warnings)
        detailed_scores["credit_history"] = credit_score

        payment_score, payment_warnings = self.assess_payment_capacity(
            request.annual_income,
            request.other_income_sources,
            monthly_payment,
            request.number_of_dependents,
        )

        all_warnings.extend(payment_warnings)
        detailed_scores["payment_capacity"] = payment_score

        debt_score, debt_warnings = self.assess_debt_burden(
            request.current_debt_to_income_ratio, request.annual_income
        )

        all_warnings.extend(debt_warnings)
        detailed_scores["debt_burden"] = debt_score

        agri_score, agri_warnings = self.assess_agricultural_profile(
            request.years_of_agricultural_experience,
            request.farm_size_hectares,
            request.has_agricultural_insurance,
            request.annual_income,
        )

        all_warnings.extend(agri_warnings)
        detailed_scores["agricultural_profile"] = agri_score

        demo_score, demo_warnings = self.assess_demographics(age)

        all_warnings.extend(demo_warnings)
        detailed_scores["demographics"] = demo_score

        collateral_score, collateral_warnings = self.assess_collateral(
            request.has_collateral,
            request.collateral_value or 0,
            request.requested_amount,
        )

        all_warnings.extend(collateral_warnings)
        detailed_scores["collateral"] = collateral_score

        loan_score, loan_warnings = self.assess_loan_characteristics(
            request.requested_amount,
            request.term_months,
            request.annual_income,
            request.applicant_contribution_amount,
        )

        all_warnings.extend(loan_warnings)
        detailed_scores["loan_characteristics"] = loan_score

        total_positive_score = (
            (credit_score * self.WEIGHTS["credit_history"] / 100)
            + (payment_score * self.WEIGHTS["payment_capacity"] / 100)
            + (debt_score * self.WEIGHTS["debt_burden"] / 100)
            + (agri_score * self.WEIGHTS["agricultural_profile"] / 100)
            + (demo_score * self.WEIGHTS["demographics"] / 100)
            + (collateral_score * self.WEIGHTS["collateral"] / 100)
            + (loan_score * self.WEIGHTS["loan_characteristics"] / 100)
        )

        risk_percentage = max(0, min(100, 100 - total_positive_score))

        if risk_percentage <= 15:
            risk_level = RiskLevel.VERY_LOW
        elif risk_percentage <= 25:
            risk_level = RiskLevel.LOW
        elif risk_percentage <= 40:
            risk_level = RiskLevel.MEDIUM
        elif risk_percentage <= 60:
            risk_level = RiskLevel.HIGH
        elif risk_percentage <= 80:
            risk_level = RiskLevel.VERY_HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        approval_recommendation = risk_level in [
            RiskLevel.VERY_LOW,
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
        ]

        risk_multiplier = 1.0
        if risk_level == RiskLevel.VERY_LOW:
            risk_multiplier = 1.0
        elif risk_level == RiskLevel.LOW:
            risk_multiplier = 0.9
        elif risk_level == RiskLevel.MEDIUM:
            risk_multiplier = 0.7
        elif risk_level == RiskLevel.HIGH:
            risk_multiplier = 0.5
        else:
            risk_multiplier = 0.2

        max_recommended = min(
            request.requested_amount * risk_multiplier, request.annual_income * 3
        )

        base_rate = self.BASE_RATES[risk_level]
        recommended_rate = base_rate + (risk_percentage * 0.1)
        return RiskAssessmentResult(
            risk_score=risk_percentage,
            risk_level=risk_level,
            risk_percentage=risk_percentage,
            approval_recommendation=approval_recommendation,
            maximum_recommended_amount=max_recommended,
            recommended_interest_rate=min(recommended_rate, 40.0),
            detailed_analysis={
                "scores_by_category": detailed_scores,
                "weights_applied": self.WEIGHTS,
                "age_calculated": age,
                "monthly_payment": monthly_payment,
                "payment_to_income_ratio": (
                    (monthly_payment * 12) / request.annual_income
                    if request.annual_income > 0
                    else 0
                ),
                "total_positive_score": total_positive_score,
                "final_risk_score": risk_percentage,
            },
            warning_flags=all_warnings,
        )
