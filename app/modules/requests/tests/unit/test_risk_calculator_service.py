import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# Import the service class and its dependencies
# Asegúrate de ajustar estas rutas de importación según tu estructura de proyecto
from app.modules.requests.services.calculate_risk_service import ( # Asumiendo esta ruta para el servicio
    CreditRiskCalculator,
    CreditRequest,
    RiskAssessmentResult,
    RiskLevel,
)


# --- Fixtures ---

@pytest.fixture
def credit_risk_calculator():
    """Provee una instancia de CreditRiskCalculator."""
    return CreditRiskCalculator()

# --- Tests para métodos estáticos ---

@patch('app.modules.requests.services.calculate_risk_service.datetime')
def test_calculate_age_exact_birthday(mock_datetime):
    """
    Testea calculate_age cuando la fecha actual es exactamente el cumpleaños.
    """
    mock_datetime.now.return_value.date.return_value = date(2024, 5, 15)
    birth_date = date(1990, 5, 15)
    assert CreditRiskCalculator.calculate_age(birth_date) == 34

@patch('app.modules.requests.services.calculate_risk_service.datetime')
def test_calculate_age_before_birthday(mock_datetime):
    """
    Testea calculate_age cuando la fecha actual es antes del cumpleaños.
    """
    mock_datetime.now.return_value.date.return_value = date(2024, 5, 14)
    birth_date = date(1990, 5, 15)
    assert CreditRiskCalculator.calculate_age(birth_date) == 33

@patch('app.modules.requests.services.calculate_risk_service.datetime')
def test_calculate_age_after_birthday(mock_datetime):
    """
    Testea calculate_age cuando la fecha actual es después del cumpleaños.
    """
    mock_datetime.now.return_value.date.return_value = date(2024, 5, 16)
    birth_date = date(1990, 5, 15)
    assert CreditRiskCalculator.calculate_age(birth_date) == 34

@patch('app.modules.requests.services.calculate_risk_service.datetime')
def test_calculate_age_leap_year(mock_datetime):
    """
    Testea calculate_age con un año bisiesto.
    """
    mock_datetime.now.return_value.date.return_value = date(2025, 2, 28)
    birth_date = date(1996, 2, 29) # Nació en año bisiesto
    assert CreditRiskCalculator.calculate_age(birth_date) == 28

@patch('app.modules.requests.services.calculate_risk_service.datetime')
def test_calculate_age_different_years(mock_datetime):
    """
    Testea calculate_age con una diferencia de años significativa.
    """
    mock_datetime.now.return_value.date.return_value = date(2024, 1, 1)
    birth_date = date(1970, 1, 1)
    assert CreditRiskCalculator.calculate_age(birth_date) == 54

@patch('app.modules.requests.services.calculate_risk_service.datetime')
def test_calculate_monthly_payment_valid_inputs(mock_datetime):
    """
    Testea calculate_monthly_payment con entradas válidas.
    """
    # Ejemplo: $100,000 a 5% anual por 12 meses
    principal = 100000
    annual_rate = 5.0
    months = 12
    # Valor esperado calculado con una calculadora de préstamos
    expected_payment = 8560.75 # Aprox.
    assert CreditRiskCalculator.calculate_monthly_payment(principal, annual_rate, months) == pytest.approx(expected_payment, rel=1e-2)


def test_calculate_monthly_payment_zero_months():
    """
    Testea calculate_monthly_payment con cero meses.
    """
    assert CreditRiskCalculator.calculate_monthly_payment(100000, 5, 0) == 0

def test_calculate_monthly_payment_negative_rate():
    """
    Testea calculate_monthly_payment con tasa de interés negativa.
    """
    assert CreditRiskCalculator.calculate_monthly_payment(100000, -5, 12) == 0

def test_calculate_monthly_payment_large_values():
    """
    Testea calculate_monthly_payment con valores grandes.
    """
    principal = 1000000000
    annual_rate = 10.0
    months = 360 # 30 años
    expected_payment = 8775717.30 # Aprox.
    assert CreditRiskCalculator.calculate_monthly_payment(principal, annual_rate, months) == pytest.approx(expected_payment, rel=1e-2)

# --- Tests para métodos de evaluación de riesgo ---

def test_assess_credit_history_excellent_score_no_defaults(credit_risk_calculator):
    """
    Testea assess_credit_history con puntaje excelente y sin incumplimientos.
    """
    score, warnings = credit_risk_calculator.assess_credit_history(800, 0)
    assert score == 100
    assert warnings == []

def test_assess_credit_history_low_score_one_default(credit_risk_calculator):
    """
    Testea assess_credit_history con puntaje bajo y un incumplimiento.
    """
    score, warnings = credit_risk_calculator.assess_credit_history(560, 1)
    assert score == 32 # 20 (score) + 12 (defaults)
    assert "Puntaje crediticio por debajo del promedio" in warnings
    assert "Un incumplimiento previo registrado" in warnings

def test_assess_credit_history_very_low_score_multiple_defaults(credit_risk_calculator):
    """
    Testea assess_credit_history con puntaje muy bajo y múltiples incumplimientos.
    """
    score, warnings = credit_risk_calculator.assess_credit_history(400, 3)
    assert score == 4 # 4 (score) + 0 (defaults)
    assert "Puntaje crediticio muy bajo - alto riesgo" in warnings
    assert "Historial de múltiples incumplimientos - riesgo crítico" in warnings

def test_assess_payment_capacity_high_income_low_payment_no_dependents(credit_risk_calculator):
    """
    Testea assess_payment_capacity con altos ingresos, cuota baja y sin dependientes.
    """
    score, warnings = credit_risk_calculator.assess_payment_capacity(
        annual_income=100_000_000, other_income=10_000_000, monthly_payment=500_000, dependents=0
    )
    assert score == 95
    assert warnings == []

def test_assess_payment_capacity_low_income_high_payment_many_dependents(credit_risk_calculator):
    """
    Testea assess_payment_capacity con bajos ingresos, cuota alta y muchos dependientes.
    """
    score, warnings = credit_risk_calculator.assess_payment_capacity(
        annual_income=20_000_000, other_income=0, monthly_payment=1_500_000, dependents=5
    )
    assert score == 10
    assert "Cuota mensual excesiva respecto al ingreso - riesgo muy alto" in warnings
    assert "Ingresos bajos para el monto solicitado" in warnings
    assert "Alto número de dependientes reduce capacidad de pago" in warnings

def test_assess_debt_burden_low_ratio(credit_risk_calculator):
    """
    Testea assess_debt_burden con una relación deuda-ingreso baja.
    """
    score, warnings = credit_risk_calculator.assess_debt_burden(0.15, 50_000_000)
    assert score == 100
    assert warnings == []

def test_assess_debt_burden_high_ratio(credit_risk_calculator):
    """
    Testea assess_debt_burden con una relación deuda-ingreso alta.
    """
    score, warnings = credit_risk_calculator.assess_debt_burden(0.55, 50_000_000)
    assert score == 7
    assert "Nivel de endeudamiento crítico" in warnings

def test_assess_agricultural_profile_experienced_insured_high_productivity(credit_risk_calculator):
    """
    Testea assess_agricultural_profile con experiencia, seguro y alta productividad.
    """
    score, warnings = credit_risk_calculator.assess_agricultural_profile(
        experience_years=20, farm_size=10, has_insurance=True, annual_income=60_000_000
    )
    assert score == 100 # 42 (exp) + 33 (prod) + 25 (insurance)
    assert warnings == []

def test_assess_agricultural_profile_limited_experience_no_insurance_low_productivity(credit_risk_calculator):
    """
    Testea assess_agricultural_profile con experiencia limitada, sin seguro y baja productividad.
    """
    score, warnings = credit_risk_calculator.assess_agricultural_profile(
        experience_years=1, farm_size=5, has_insurance=False, annual_income=1_000_000
    )
    assert score == 8 # 4 (exp) + 4 (prod) + 0 (insurance)
    assert "Experiencia agrícola limitada aumenta el riesgo" in warnings
    assert "Baja productividad por hectárea" in warnings
    assert "Sin seguro agrícola - mayor exposición a riesgos climáticos" in warnings

def test_assess_demographics_optimal_age(credit_risk_calculator):
    """
    Testea assess_demographics con una edad óptima.
    """
    score, warnings = credit_risk_calculator.assess_demographics(40)
    assert score == 100
    assert warnings == []

def test_assess_demographics_young_age(credit_risk_calculator):
    """
    Testea assess_demographics con una edad joven.
    """
    score, warnings = credit_risk_calculator.assess_demographics(10)
    assert score == 25
    assert "Edad joven puede indicar falta de experiencia" in warnings

def test_assess_demographics_old_age(credit_risk_calculator):
    """
    Testea assess_demographics con una edad avanzada.
    """
    score, warnings = credit_risk_calculator.assess_demographics(75)
    assert score == 25
    assert "Edad avanzada puede afectar capacidad de trabajo" in warnings

def test_assess_collateral_no_collateral(credit_risk_calculator):
    """
    Testea assess_collateral sin garantías.
    """
    score, warnings = credit_risk_calculator.assess_collateral(False, 0, 100000)
    assert score == 0
    assert "Sin garantías reales - mayor riesgo para la entidad" in warnings

def test_assess_collateral_full_coverage(credit_risk_calculator):
    """
    Testea assess_collateral con cobertura total.
    """
    score, warnings = credit_risk_calculator.assess_collateral(True, 150000, 100000)
    assert score == 100
    assert warnings == []

def test_assess_collateral_insufficient_coverage(credit_risk_calculator):
    """
    Testea assess_collateral con cobertura insuficiente.
    """
    score, warnings = credit_risk_calculator.assess_collateral(True, 70000, 100000)
    assert score == 20
    assert "Garantía baja respecto al monto solicitado" in warnings

def test_assess_loan_characteristics_low_amount_short_term_high_contribution(credit_risk_calculator):
    """
    Testea assess_loan_characteristics con monto bajo, plazo corto y alta contribución.
    """
    score, warnings = credit_risk_calculator.assess_loan_characteristics(
        requested_amount=50_000_000, term_months=24, annual_income=30_000_000, contribution=10_000_000
    )
    assert score == 95
    assert warnings == []

def test_assess_loan_characteristics_high_amount_long_term_low_contribution(credit_risk_calculator):
    """
    Testea assess_loan_characteristics con monto alto, plazo largo y baja contribución.
    """
    score, warnings = credit_risk_calculator.assess_loan_characteristics(
        requested_amount=500_000_000, term_months=220, annual_income=3_000_000, contribution=0
    )
    assert score == 15
    assert "Monto muy alto respecto a capacidad de ingresos" in warnings
    assert "Plazo muy largo aumenta riesgo de incumplimiento" in warnings
    assert "Bajo aporte propio aumenta el riesgo" in warnings

# --- Tests para calculate_risk_score (método principal) ---

@patch.object(CreditRiskCalculator, 'calculate_age')
@patch.object(CreditRiskCalculator, 'calculate_monthly_payment')
@patch.object(CreditRiskCalculator, 'assess_credit_history')
@patch.object(CreditRiskCalculator, 'assess_payment_capacity')
@patch.object(CreditRiskCalculator, 'assess_debt_burden')
@patch.object(CreditRiskCalculator, 'assess_agricultural_profile')
@patch.object(CreditRiskCalculator, 'assess_demographics')
@patch.object(CreditRiskCalculator, 'assess_collateral')
@patch.object(CreditRiskCalculator, 'assess_loan_characteristics')
def test_calculate_risk_score_low_risk_scenario(
    mock_loan_characteristics, mock_collateral, mock_demographics, mock_agricultural_profile,
    mock_debt_burden, mock_payment_capacity, mock_credit_history,
    mock_calculate_monthly_payment, mock_calculate_age,
    credit_risk_calculator
):
    """
    Testea calculate_risk_score para un escenario de bajo riesgo.
    Se mokean los métodos de evaluación individuales para aislar la lógica de cálculo principal.
    """
    # Mockear los resultados de los métodos de evaluación individuales
    mock_calculate_age.return_value = 40
    mock_calculate_monthly_payment.return_value = 500_000

    mock_credit_history.return_value = (90, [])
    mock_payment_capacity.return_value = (85, [])
    mock_debt_burden.return_value = (95, [])
    mock_agricultural_profile.return_value = (80, [])
    mock_demographics.return_value = (100, [])
    mock_collateral.return_value = (90, [])
    mock_loan_characteristics.return_value = (80, [])

    # Crear una solicitud de crédito de ejemplo
    credit_request = CreditRequest(
        date_of_birth=date(1984, 1, 1),
        annual_income=100_000_000,
        years_of_agricultural_experience=15,
        has_agricultural_insurance=True,
        internal_credit_history_score=800,
        current_debt_to_income_ratio=0.15,
        farm_size_hectares=20.0,
        requested_amount=50_000_000,
        term_months=60,
        annual_interest_rate=10.0,
        applicant_contribution_amount=10_000_000,
        has_collateral=True,
        collateral_value=75_000_000,
        number_of_dependents=0,
        other_income_sources=5_000_000,
        previous_defaults=0,
    )

    result = credit_risk_calculator.calculate_risk_score(credit_request)

    # Verificar que los métodos internos fueron llamados
    mock_calculate_age.assert_called_once_with(credit_request.date_of_birth)
    mock_calculate_monthly_payment.assert_called_once_with(
        credit_request.requested_amount, credit_request.annual_interest_rate, credit_request.term_months
    )
    mock_credit_history.assert_called_once()
    mock_payment_capacity.assert_called_once()
    mock_debt_burden.assert_called_once()
    mock_agricultural_profile.assert_called_once()
    mock_demographics.assert_called_once()
    mock_collateral.assert_called_once()
    mock_loan_characteristics.assert_called_once()

    # Asertar los resultados esperados para un escenario de bajo riesgo
    assert result.risk_level == RiskLevel.VERY_LOW
    assert result.approval_recommendation is True
    assert result.risk_score == pytest.approx(100 - (
        (90 * 0.25) + (85 * 0.20) + (95 * 0.15) + (80 * 0.12) +
        (100 * 0.08) + (90 * 0.10) + (80 * 0.10)
    ), rel=1e-2) # Calcula el puntaje total positivo
    assert result.risk_percentage == pytest.approx(result.risk_score, rel=1e-2)
    assert result.recommended_interest_rate == pytest.approx(12.0 + (result.risk_percentage * 0.1), rel=1e-2)
    assert result.warning_flags == []
    assert "scores_by_category" in result.detailed_analysis

@patch.object(CreditRiskCalculator, 'calculate_age')
@patch.object(CreditRiskCalculator, 'calculate_monthly_payment')
@patch.object(CreditRiskCalculator, 'assess_credit_history')
@patch.object(CreditRiskCalculator, 'assess_payment_capacity')
@patch.object(CreditRiskCalculator, 'assess_debt_burden')
@patch.object(CreditRiskCalculator, 'assess_agricultural_profile')
@patch.object(CreditRiskCalculator, 'assess_demographics')
@patch.object(CreditRiskCalculator, 'assess_collateral')
@patch.object(CreditRiskCalculator, 'assess_loan_characteristics')
def test_calculate_risk_score_high_risk_scenario(
    mock_loan_characteristics, mock_collateral, mock_demographics, mock_agricultural_profile,
    mock_debt_burden, mock_payment_capacity, mock_credit_history,
    mock_calculate_monthly_payment, mock_calculate_age,
    credit_risk_calculator
):
    """
    Testea calculate_risk_score para un escenario de alto riesgo.
    """
    # Mockear los resultados de los métodos de evaluación individuales para un escenario de alto riesgo
    mock_calculate_age.return_value = 22
    mock_calculate_monthly_payment.return_value = 2_000_000 # Cuota alta

    mock_credit_history.return_value = (10, ["Puntaje crediticio muy bajo - alto riesgo"])
    mock_payment_capacity.return_value = (15, ["Cuota mensual excesiva respecto al ingreso - riesgo muy alto"])
    mock_debt_burden.return_value = (5, ["Nivel de endeudamiento crítico"])
    mock_agricultural_profile.return_value = (10, ["Experiencia agrícola limitada aumenta el riesgo"])
    mock_demographics.return_value = (25, ["Edad joven puede indicar falta de experiencia"])
    mock_collateral.return_value = (0, ["Sin garantías reales - mayor riesgo para la entidad"])
    mock_loan_characteristics.return_value = (10, ["Monto muy alto respecto a capacidad de ingresos"])

    # Crear una solicitud de crédito de ejemplo para alto riesgo
    credit_request = CreditRequest(
        date_of_birth=date(2002, 1, 1),
        annual_income=25_000_000,
        years_of_agricultural_experience=1,
        has_agricultural_insurance=False,
        internal_credit_history_score=400,
        current_debt_to_income_ratio=0.70,
        farm_size_hectares=2.0,
        requested_amount=150_000_000,
        term_months=180,
        annual_interest_rate=30.0,
        applicant_contribution_amount=0,
        has_collateral=False,
        collateral_value=0,
        number_of_dependents=3,
        other_income_sources=0,
        previous_defaults=2,
    )

    result = credit_risk_calculator.calculate_risk_score(credit_request)

    # Asertar los resultados esperados para un escenario de alto riesgo
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.approval_recommendation is False
    assert result.risk_score == pytest.approx(100 - (
        (10 * 0.25) + (15 * 0.20) + (5 * 0.15) + (10 * 0.12) +
        (25 * 0.08) + (0 * 0.10) + (10 * 0.10)
    ), rel=1e-2)
    assert result.risk_percentage == pytest.approx(result.risk_score, rel=1e-2)
    assert result.recommended_interest_rate == pytest.approx(31.0 + (result.risk_percentage * 0.1), rel=1e-2)
    assert "Puntaje crediticio muy bajo - alto riesgo" in result.warning_flags
    assert "Cuota mensual excesiva respecto al ingreso - riesgo muy alto" in result.warning_flags
    assert "Nivel de endeudamiento crítico" in result.warning_flags
    assert "Experiencia agrícola limitada aumenta el riesgo" in result.warning_flags
    assert "Edad joven puede indicar falta de experiencia" in result.warning_flags
    assert "Sin garantías reales - mayor riesgo para la entidad" in result.warning_flags
    assert "Monto muy alto respecto a capacidad de ingresos" in result.warning_flags
    assert "scores_by_category" in result.detailed_analysis

