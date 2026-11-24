from datetime import date, datetime
from flask import Blueprint, render_template, request, make_response, current_app
from flask_login import login_required, current_user

from app.services.report_service import ReportService

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("")
@reports_bp.route("/")
@login_required
def index():
    report_type = request.args.get("report_type", "annual_summary")
    start_date_str = request.args.get("start_date", "")
    end_date_str = request.args.get("end_date", "")
    year = request.args.get("year", date.today().year, type=int)
    month = request.args.get("month", date.today().month, type=int)

    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    report_data = ReportService.get_report_data(
        user_id=current_user.id,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        year=year,
        month=month
    )

    return render_template(
        "reports/index.html",
        report_data=report_data,
        report_type=report_type,
        start_date=start_date_str or (date(date.today().year, 1, 1).strftime("%Y-%m-%d")),
        end_date=end_date_str or date.today().strftime("%Y-%m-%d"),
        year=year,
        month=month
    )


@reports_bp.route("/export/csv")
@login_required
def export_csv():
    report_type = request.args.get("report_type", "annual_summary")
    start_date_str = request.args.get("start_date", "")
    end_date_str = request.args.get("end_date", "")
    year = request.args.get("year", date.today().year, type=int)
    month = request.args.get("month", date.today().month, type=int)

    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    report_data = ReportService.get_report_data(
        user_id=current_user.id,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        year=year,
        month=month
    )

    csv_data = ReportService.generate_csv(report_data)
    filename = f"{report_type}_{date.today().strftime('%Y%m%d')}.csv"

    response = make_response(csv_data)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response


@reports_bp.route("/export/pdf")
@login_required
def export_pdf():
    report_type = request.args.get("report_type", "annual_summary")
    start_date_str = request.args.get("start_date", "")
    end_date_str = request.args.get("end_date", "")
    year = request.args.get("year", date.today().year, type=int)
    month = request.args.get("month", date.today().month, type=int)

    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    report_data = ReportService.get_report_data(
        user_id=current_user.id,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        year=year,
        month=month
    )

    symbol = current_user.settings.currency_symbol if current_user.settings else "₹"
    pdf_bytes = ReportService.generate_pdf(report_data, currency_symbol=symbol)
    filename = f"{report_type}_{date.today().strftime('%Y%m%d')}.pdf"

    response = make_response(pdf_bytes)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/pdf"
    return response
