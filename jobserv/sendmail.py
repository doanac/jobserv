import contextlib
import logging
import smtplib

from email.mime.text import MIMEText

from flask import url_for

from jobserv.jsend import ApiError
from jobserv.models import Build, BuildStatus
from jobserv.settings import (
    BUILD_URL_FMT,
    RUN_URL_FMT,
    SMTP_SERVER,
    SMTP_USER,
    SMTP_PASSWORD,
)

log = logging.getLogger('jobserv.flask')


def build_url(build):
    if BUILD_URL_FMT:
        return BUILD_URL_FMT.format(
            project=build.project.name, build=build.build_id)

    return url_for('api_build.build_get',
                   proj=build.project.name, build_id=build.build_id)


def run_url(run):
    if RUN_URL_FMT:
        return RUN_URL_FMT.format(project=run.build.project.name,
                                  build=run.build.build_id, run=run.name)

    return url_for('api_run.run_get_artifact', proj=run.build.project.name,
                   build_id=run.build.build_id, run=run.name,
                   path='console.log', external=True)


@contextlib.contextmanager
def smtp_session():
    s = smtplib.SMTP(SMTP_SERVER, 587)
    rv, msg = s.starttls()
    if rv != 220:
        log.error('Unable to connect to SMTP server %s: %d %s',
                  SMTP_SERVER, rv, msg.decode())
        raise ApiError(500, 'Unable to connect to SMTP server')
    rv, msg = s.login(SMTP_USER, SMTP_PASSWORD)
    if rv != 235:
        log.error('Unable to authenticate with SMTP server %s: %d %s',
                  SMTP_SERVER, rv, msg.decode())
        raise ApiError(500, 'Unable to authenticate with SMTP server')
    try:
        yield s
    finally:
        s.quit()


def _get_build_stats(build):
    '''Look at last 20 builds to see how things have been doing'''
    complete = (BuildStatus.PASSED, BuildStatus.FAILED)
    query = Build.query.filter(
        Build.proj_id == build.proj_id,
        Build.id <= build.id,
        Build.status.in_(complete)
    ).order_by(
        Build.id.desc()
    ).limit(20)

    b_stats = {
        'passes': 0,
        'total': 0,
        'pass_fails': '',
    }
    for b in query:
        if b.status == BuildStatus.PASSED:
            b_stats['passes'] += 1
            b_stats['pass_fails'] += '+'
        else:
            b_stats['pass_fails'] += '-'
        b_stats['total'] += 1
    b_stats['pass_rate'] = int((b_stats['passes'] / b_stats['total']) * 100)
    return b_stats


def notify_build_complete(build, to_list):
    subject = 'jobserv: %s build #%d : %s' % (
        build.project.name, build.build_id, build.status.name)
    body = subject + '\n'
    body += 'Build URL: %s\n\n' % build_url(build)

    body += 'Runs:\n'
    for run in build.runs:
        url = run_url(run)
        body += '  %s: %s\n    %s\n' % (run.name, run.status.name, url)
    if build.reason:
        body += '\nReason:\n' + build.reason

    stats = _get_build_stats(build)
    body += '''Build history for last {total} builds:
  pass rate: {pass_rate}%
   (newest->oldest): {pass_fails}
    '''.format(**stats)

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'Do Not Reply <donot-reply@linaro.org>'
    msg['To'] = to_list
    with smtp_session() as s:
        s.send_message(msg)