# flake8: noqa: F541
from app.shared.entities.requestEntity import Request
from datetime import datetime
from typing import Optional


class TemplateService:
    def __init__(self):
        self.brand_color = "#16a34a"
        self.brand_color_light = "#dcfce7"
        self.brand_color_dark = "#15803d"
        self.error_color = "#dc2626"
        self.warning_color = "#f59e0b"
        self.base_url = "https://app.agricapital.co"

    def _get_base_styles(self) -> str:
        """Estilos base para todos los templates"""
        return f"""
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #374151;
                background-color: #f9fafb;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, {self.brand_color} 0%, {self.brand_color_dark} 100%);
                padding: 32px 24px;
                text-align: center;
                color: white;
            }}
            .header h1 {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 8px;
            }}
            .header .subtitle {{
                font-size: 18px;
                opacity: 0.9;
            }}
            .content {{
                padding: 32px 24px;
            }}
            .greeting {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 16px;
                color: #111827;
            }}
            .message {{
                font-size: 16px;
                margin-bottom: 24px;
                color: #6b7280;
            }}
            .card {{
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 24px;
                margin: 24px 0;
            }}
            .card-title {{
                font-size: 18px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
            }}
            .card-title::before {{
                content: "📄";
                margin-right: 8px;
            }}
            .details-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin-bottom: 16px;
            }}
            .detail-item {{
                padding: 12px;
                background-color: white;
                border-radius: 6px;
                border-left: 4px solid {self.brand_color};
            }}
            .detail-label {{
                font-size: 12px;
                font-weight: 500;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }}
            .detail-value {{
                font-size: 16px;
                font-weight: 600;
                color: #111827;
            }}
            .detail-value.highlight {{
                color: {self.brand_color};
                font-size: 18px;
            }}
            .btn {{
                display: inline-block;
                padding: 14px 28px;
                background: linear-gradient(135deg, {self.brand_color} 0%, {self.brand_color_dark} 100%);
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 16px;
                text-align: center;
                transition: all 0.3s ease;
                margin: 16px 0;
            }}
            .btn:hover {{
                background: {self.brand_color_dark};
                transform: translateY(-1px);
            }}
            .btn-secondary {{
                background: white;
                color: {self.brand_color};
                border: 2px solid {self.brand_color};
            }}
            .info-box {{
                background-color: {self.brand_color_light};
                border: 1px solid {self.brand_color};
                border-radius: 8px;
                padding: 20px;
                margin: 24px 0;
            }}
            .info-box h4 {{
                color: {self.brand_color_dark};
                font-weight: 600;
                margin-bottom: 8px;
            }}
            .info-box ul {{
                margin: 0;
                padding-left: 20px;
                color: {self.brand_color_dark};
            }}
            .footer {{
                background-color: #f3f4f6;
                padding: 24px;
                text-align: center;
                border-top: 1px solid #e5e7eb;
            }}
            .footer p {{
                font-size: 14px;
                color: #6b7280;
                margin-bottom: 8px;
            }}
            .contact-info {{
                font-size: 12px;
                color: #9ca3af;
            }}
            .status-badge {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .status-pending {{
                background-color: {self.brand_color_light};
                color: {self.brand_color_dark};
            }}
            .status-approved {{
                background-color: #dcfce7;
                color: #166534;
            }}
            .status-rejected {{
                background-color: #fef2f2;
                color: #991b1b;
            }}
            @media only screen and (max-width: 600px) {{
                .email-container {{
                    margin: 0;
                    border-radius: 0;
                }}
                .header {{
                    padding: 24px 16px;
                }}
                .content {{
                    padding: 24px 16px;
                }}
                .details-grid {{
                    grid-template-columns: 1fr;
                }}
                .btn {{
                    display: block;
                    width: 100%;
                }}
            }}
        </style>
        """

    def _format_currency(self, amount: Optional[float]) -> str:
        """Formatea montos en pesos colombianos"""
        if amount is None:
            return "N/A"
        return f"${amount:,.0f} COP"

    def _format_date(self, date: Optional[datetime]) -> str:
        """Formatea fechas en español"""
        if date is None:
            return "Fecha no disponible"

        months = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]

        return f"{date.day} de {months[date.month - 1]} de {date.year}"

    def _get_footer(self) -> str:
        """Footer común para todos los templates"""
        return f"""
        <div class="footer">
            <p><strong>AgriCapital</strong> - Impulsando el futuro agrícola de Colombia</p>
            <div class="contact-info">
                <p>📞 +57 (1) 234-5678 | ✉️ soporte@agricapital.co</p>
                <p>🌐 www.agricapital.co</p>
                <p style="margin-top: 16px;">© 2025 AgriCapital. Todos los derechos reservados.</p>
            </div>
        </div>
        """

    def request_sent(
        self, request: Request, user_name: str = "Estimado/a cliente"
    ) -> str:
        """Template para solicitud enviada"""
        monto = self._format_currency(request.requested_amount)
        fecha = self._format_date(request.created_at)
        tasa = (
            f"{request.annual_interest_rate:.1f}%"
            if request.annual_interest_rate
            else "N/A"
        )

        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Solicitud de Crédito Enviada - AgriCapital</title>
            {self._get_base_styles()}
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🌱 AgriCapital</h1>
                    <div class="subtitle">¡Solicitud Recibida!</div>
                </div>

                <div class="content">
                    <div class="greeting">Hola {user_name},</div>

                    <p class="message">
                        Hemos recibido tu solicitud de crédito y ya estamos trabajando en su evaluación.
                        Nuestro equipo especializado revisará tu perfil agrícola en las próximas 24-48 horas.
                    </p>

                    <span class="status-badge status-pending">⏳ En Proceso</span>

                    <div class="card">
                        <div class="card-title">Detalles de tu Solicitud</div>

                        <div class="details-grid">
                            <div class="detail-item">
                                <div class="detail-label">Número de Solicitud</div>
                                <div class="detail-value">#{request.id}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Fecha de Solicitud</div>
                                <div class="detail-value">{fecha}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Monto Solicitado</div>
                                <div class="detail-value highlight">{monto}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Plazo</div>
                                <div class="detail-value">{request.term_months} meses</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Tasa de Interés</div>
                                <div class="detail-value">{tasa}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Tipo de Crédito</div>
                                <div class="detail-value">Inversión Agrícola</div>
                            </div>
                        </div>
                    </div>

                    <div class="info-box">
                        <h4>⏰ ¿Qué sigue ahora?</h4>
                        <ul>
                            <li>Nuestro equipo evaluará tu solicitud en las próximas 24-48 horas</li>
                            <li>Recibirás una respuesta por email y SMS</li>
                            <li>Si necesitamos información adicional, te contactaremos</li>
                        </ul>
                    </div>

                    <p style="margin-top: 32px; font-size: 14px; color: #6b7280;">
                        <strong>¿Tienes preguntas?</strong> Nuestro equipo de soporte está disponible para ayudarte
                        de lunes a viernes de 8:00 AM a 6:00 PM.
                    </p>
                </div>

                {self._get_footer()}
            </div>
        </body>
        </html>
        """

    def request_approved(
        self,
        request: Request,
        user_name: str = "Estimado/a cliente",
        approved_amount: Optional[float] = None,
    ) -> str:
        """Template para solicitud aprobada"""
        approved_amount = self._format_currency(approved_amount or 0)
        date = self._format_date(datetime.now())
        interest_rate = (
            f"{request.annual_interest_rate:.1f}%"
            if request.annual_interest_rate
            else "N/A"
        )

        if approved_amount and request.annual_interest_rate and request.term_months:
            monthly_rate = request.annual_interest_rate / 100 / 12
            monthly_payment = (
                approved_amount
                * monthly_rate
                * (1 + monthly_rate) ** request.term_months
            ) / ((1 + monthly_rate) ** request.term_months - 1)
            monthly_payment = self._format_currency(monthly_payment)
        else:
            monthly_payment = "A calcular"

        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>¡Crédito Aprobado! - AgriCapital</title>
            {self._get_base_styles()}
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🌱 AgriCapital</h1>
                    <div class="subtitle">¡Felicitaciones! 🎉</div>
                </div>

                <div class="content">
                    <div class="greeting">¡Excelentes noticias, {user_name}!</div>

                    <p class="message">
                        Tu solicitud de crédito ha sido <strong>aprobada</strong>. Estamos emocionados de ser parte
                        de tu proyecto agrícola y contribuir al crecimiento de tu negocio.
                    </p>

                    <span class="status-badge status-approved">✅ Aprobado</span>

                    <div class="card">
                        <div class="card-title">💰 Detalles de tu Crédito Aprobado</div>

                        <div class="details-grid">
                            <div class="detail-item">
                                <div class="detail-label">Número de Crédito</div>
                                <div class="detail-value">#{request.id}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Fecha de Aprobación</div>
                                <div class="detail-value">{date}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Monto Aprobado</div>
                                <div class="detail-value highlight">{approved_amount}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Tasa de Interés</div>
                                <div class="detail-value">{interest_rate}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Plazo</div>
                                <div class="detail-value">{request.term_months} meses</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Cuota Mensual</div>
                                <div class="detail-value highlight">{monthly_payment}</div>
                            </div>
                        </div>
                    </div>

                    <div class="info-box">
                        <h4>📋 Próximos Pasos</h4>
                        <ul>
                            <li><strong>Paso 1:</strong> Recibirás el contrato por email en las próximas 2 horas</li>
                            <li><strong>Paso 2:</strong> Firma digitalmente el contrato</li>
                            <li><strong>Paso 3:</strong> Confirma los datos de tu cuenta bancaria</li>
                            <li><strong>Paso 4:</strong> Recibe el desembolso en máximo 24 horas</li>
                        </ul>
                    </div>

                    <p style="margin-top: 32px; font-size: 14px; color: #6b7280;">
                        <strong>🤝 Acompañamiento Continuo:</strong> Nuestro equipo de asesores agrícolas estará
                        disponible para apoyarte durante todo el proceso y el desarrollo de tu proyecto.
                    </p>
                </div>

                {self._get_footer()}
            </div>
        </body>
        </html>
        """

    def request_rejected(
        self,
        request: Request,
        user_name: str = "Estimado/a cliente",
        rejection_reason: str = "No cumple con los criterios de evaluación actuales",
    ) -> str:
        """Template para solicitud rechazada"""
        monto = self._format_currency(request.requested_amount)
        fecha = self._format_date(datetime.now())

        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resultado de tu Solicitud - AgriCapital</title>
            {self._get_base_styles()}
            <style>
                .rejection-header {{
                    background: linear-gradient(135deg, {self.error_color} 0%, #b91c1c 100%);
                }}
                .rejection-reason {{
                    background-color: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 24px 0;
                }}
                .rejection-reason h4 {{
                    color: #991b1b;
                    font-weight: 600;
                    margin-bottom: 12px;
                }}
                .rejection-reason p {{
                    color: #7f1d1d;
                    margin-bottom: 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header rejection-header">
                    <h1>🌱 AgriCapital</h1>
                    <div class="subtitle">Resultado de tu Solicitud</div>
                </div>

                <div class="content">
                    <div class="greeting">Hola {user_name},</div>

                    <p class="message">
                        Después de evaluar cuidadosamente tu solicitud, lamentamos informarte que no podemos
                        aprobar tu crédito en este momento. Sabemos lo importante que es tu proyecto para ti.
                    </p>

                    <span class="status-badge status-rejected">❌ No Aprobada</span>

                    <div class="card">
                        <div class="card-title">📋 Detalles de la Evaluación</div>

                        <div class="details-grid">
                            <div class="detail-item">
                                <div class="detail-label">Número de Solicitud</div>
                                <div class="detail-value">#{request.id}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Fecha de Evaluación</div>
                                <div class="detail-value">{fecha}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Monto Solicitado</div>
                                <div class="detail-value">{monto}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Plazo</div>
                                <div class="detail-value">{request.term_months} meses</div>
                            </div>
                        </div>
                    </div>

                    <div class="rejection-reason">
                        <h4>📝 Razón de la Decisión</h4>
                        <p>{rejection_reason}</p>
                        <p>Además, se identificaron los siguientes riesgos:</p>
                        <ul>
                            {''.join(f'<li>{flag}</li>' for flag in request.warning_flags)}
                        </ul>
                    </div>

                    <div class="info-box">
                        <h4>💚 No te desanimes, ¡podemos ayudarte!</h4>
                        <p style="margin-bottom: 12px;">Te recomendamos las siguientes alternativas:</p>
                        <ul>
                            <li>Reducir el monto solicitado</li>
                            <li>Considerar un plazo más largo</li>
                            <li>Incluir un co-deudor con ingresos adicionales</li>
                            <li>Mejorar tu perfil crediticio y volver a aplicar en 3-6 meses</li>
                            <li>Solicitar asesoría gratuita con nuestros expertos</li>
                        </ul>
                    </div>

                    <p style="margin-top: 32px; font-size: 14px; color: #6b7280;">
                        <strong>🌱 Seguimos Creyendo en Ti:</strong> Puedes volver a aplicar en cualquier momento.
                        Nuestro equipo está disponible para orientarte y ayudarte a fortalecer tu perfil crediticio.
                    </p>
                </div>

                {self._get_footer()}
            </div>
        </body>
        </html>
        """
