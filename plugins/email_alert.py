import os

from airflow.utils.email import send_email

def send_email_failure_alert(context):
    """
    Callback gui mail canh bao tu dong khi task that bai.
    """
    task_instance = context.get('task_instance')
    dag_id = task_instance.dag_id
    task_id = task_instance.task_id
    execution_date = context.get('execution_date')
    log_url = task_instance.log_url
    exception = context.get('exception')

    subject = f"[ALERT] Airflow Task Failed: {dag_id}.{task_id}"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #d9534f;">🚨 Airflow Pipeline Task Failed</h2>
        <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; width: 140px;">DAG ID</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{dag_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Task ID</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{task_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Execution Time</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{execution_date}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Error Detail</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #c7254e; background-color: #f9f2f4;">
                    <pre style="margin: 0; white-space: pre-wrap;">{str(exception)[:400]}</pre>
                </td>
            </tr>
        </table>
        <br/>
        <a href="{log_url}" style="background-color: #0275d8; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; display: inline-block;">
            Xem chi tiết Log trên Airflow
        </a>
    </div>
    """

    # Danh sach email nhan thong bao
    recipients = [
        address.strip()
        for address in os.getenv('AIRFLOW_ALERT_EMAIL_TO', '').split(',')
        if address.strip()
    ]
    if not recipients:
        print('[Email Alert] AIRFLOW_ALERT_EMAIL_TO is not configured; skipping email.')
        return

    try:
        send_email(to=recipients, subject=subject, html_content=html_content)
        print(f"[Email Alert] Da gui email canh bao cho task: {task_id}")
    except Exception as e:
        print(f"[Email Alert] Loi khi gui email: {e}")