import datetime
import json
import logging
import os
import pathlib
import re
import tempfile
from subprocess import PIPE, Popen

from appy.pod.renderer import Renderer
from django.conf import settings
from django.contrib import auth
from django.core.mail import mail_admins
from django.db.models import Q

logger = logging.getLogger("geno")


def send_error_mail(subject, msg, exception=None):
    if exception is not None:
        msg = msg + "\n\nException:\n%s" % exception
    return mail_admins(f"ERROR: {subject}", msg, fail_silently=True)


def send_info_mail(subject, msg):
    return mail_admins(f"INFO: {subject}", msg, fail_silently=True)


def odt2pdf(odtfile, instance_tag="default"):
    tmpdir = "/tmp/odt2pdf_%s_%s" % (settings.GENO_ID, instance_tag)
    soffice_bin = "/usr/lib/libreoffice/program/soffice.bin"

    path, basename = os.path.split(odtfile)
    outfile = os.path.splitext(basename)

    cmd = [
        soffice_bin,
        #'--headless',
        "-env:UserInstallation=file://%s" % tmpdir,
        "--convert-to",
        "pdf:writer_pdf_Export",
        "--outdir",
        "%s" % path,
        "%s" % odtfile,
    ]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    if p.returncode or len(err):
        if not os.path.isdir("%s/user/config/soffice.cfg" % tmpdir):
            ## Work around startup problems by trying again
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            if p.returncode or len(err):
                raise Exception("odt2pdf failed: %s - %s (2. attempt)" % (output, err))
        else:
            raise Exception("odt2pdf failed: %s - %s (1. attempt)" % (output, err))

    pdf_file = "%s/%s.pdf" % (path, outfile[0])
    if not os.path.isfile(pdf_file):
        raise Exception("odt2pdf failed")

    return pdf_file


def fill_template_pod(template, context, output_format="odt"):
    media_path = pathlib.Path(settings.MEDIA_ROOT)
    if template.startswith(str(media_path.parent)):
        ## Absoulute path starting with parent of MEDIA_ROOT
        ## (to include django-filer's smedia or other sibling folder of MEDIA_ROOT)
        template_file = template
    else:
        template_file = os.path.join(settings.BASE_DIR, "geno/templates/%s" % template)

    tmpdir = "/tmp/django_pod_%s" % settings.GENO_ID
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)
    with tempfile.NamedTemporaryFile(
        suffix=".%s" % output_format, prefix="django_pod_", dir=tmpdir, delete=False
    ) as tmp_file:
        output_filename = tmp_file.name
        tmp_file.close()
        renderer = Renderer(
            template_file, context, output_filename, overwriteExisting=True, metadata=False
        )
        renderer.run()

    return output_filename


def remove_temp_files(temp_files):
    for tmpfile in temp_files:
        try:
            os.remove(tmpfile)
            # logger.debug(f"Deleted temporary file {tmpfile}")
        except Exception as e:
            logger.warning(f"Could not remove temporary file {tmpfile}: {e}")


def ensure_dir_exists(path):
    if not os.path.isdir(path):
        os.mkdir(path)


## strict_dates:
##   - True:  Check if membership end date is not in the future and that join date is in the past.
##   - False: Only check if membership end date exists.
## date_mode:
##   - strict (default): Check if membership end date is not in the future
##                       and that join date is in the past.
##   - end_date: Only check if membership end date exists.
##   - last_year: Check membership at end of previous year
def is_member(address, date_mode="strict"):
    from .models import Member

    today = datetime.date.today()
    try:
        m = Member.objects.get(name=address)
    except Member.DoesNotExist:
        return False
    if date_mode == "strict":
        return not (m.date_leave and m.date_leave <= today or m.date_join > today)
    elif date_mode == "end_date":
        return not m.date_leave
    elif date_mode == "last_year":
        end_last_year = datetime.date(today.year - 1, 12, 31)
        return not (m.date_leave and m.date_leave <= end_last_year or m.date_join > end_last_year)
    else:
        raise Exception("Unknown date_mode argument in is_member()")


def is_renting(address, date=None):
    from .models import Child

    if date is None:
        date = datetime.date.today()
    if address.address_contracts.filter(Q(date_end=None) | Q(date_end__gt=date)).count():
        return True

    ## Check if child is part of contract
    try:
        child = Child.objects.get(name=address)
    except Child.DoesNotExist:
        return False
    return bool(child.child_contracts.filter(Q(date_end=None) | Q(date_end__gt=date)).count())


def make_username(address):
    username = None
    if address.first_name and address.name:
        username = "%s.%s" % (address.first_name.split(" ", 1)[0].lower(), address.name.lower())
    elif address.first_name:
        username = address.first_name.split(" ", 1)[0].lower()
    elif address.name:
        username = address.name.lower()

    if address.organization:
        if username:
            username = "%s.%s" % (username, address.organization.lower())
        else:
            username = address.organization.lower()

    if not username:
        if address.id:
            username = f"adr{address.id}"
        else:
            return None

    username = username.replace(" ", "")
    username = username.replace("+", "")
    username = username.replace("-", "")
    username = username.replace("_", "")
    username = username.replace("/", "")
    username = username.replace(",", "")
    username = username.replace(":", "")
    username = username.replace(";", "")
    username = username.replace("(", "")
    username = username.replace(")", "")
    username = username.replace("[", "")
    username = username.replace("]", "")
    username = username.replace("ä", "ae")
    username = username.replace("ö", "oe")
    username = username.replace("ü", "ue")
    username = username.replace("é", "e")
    username = username.replace("è", "e")
    username = username.replace("ê", "e")
    username = username.replace("ç", "c")
    username = username.replace("ć", "c")
    username = username.replace("ß", "ss")
    username = username.replace("š", "s")

    ## Add numbers if username is not unique
    unique_username = username
    suffix = 2
    UserModel = auth.get_user_model()
    while UserModel.objects.filter(username=unique_username).count():
        unique_username = "%s%d" % (username, suffix)
        suffix += 1
        if suffix > 20:
            raise RuntimeError("Too many equal usernames: %s" % unique_username)
    return unique_username


def reencode_from_iso8859(file):
    for line in file:
        yield line.decode("iso8859").encode("utf-8")


def decode_from_iso8859(file):
    for line in file:
        yield line.decode("iso8859")


def nformat(number, precision=2):
    return format(number, ",.%df" % precision).replace(",", "'")


def sanitize_filename(filename):
    normalized_filename = filename.replace("+", "-").replace("/", "-")
    return re.sub(r"[^\w\-_\.]+", "", normalized_filename)


class JSONEncoderDatetime(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        return json.JSONEncoder.default(self, o)


class JSONDecoderDatetime(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, *args, object_hook=self.object_hook, **kwargs)

    def object_hook(self, json_dict):
        for key, value in json_dict.items():
            if isinstance(value, str):
                try:
                    ## With timezone
                    json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f%z")
                except (ValueError, AttributeError):
                    try:
                        ## Without timezone
                        json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
                    except (ValueError, AttributeError):
                        pass
        return json_dict


def build_account(account_prefix, building=None, rental_units=None, contract=None):
    if (
        building is None
        and rental_units is None
        and contract
        and contract.rental_units
        and contract.rental_units.all().exists()
    ):
        rental_units = contract.rental_units.all()
    if building is None and rental_units and rental_units.first():
        building = rental_units.first().building
    if building and building.accounting_postfix:
        postfix = "%03d" % building.accounting_postfix
        return re.sub(r"(\d+)$", r"\1%s" % postfix, account_prefix)
    else:
        return account_prefix
