"""
mdapi
Copyright (C) 2015-2022 Red Hat, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Any Red Hat trademarks that are incorporated in the source
code or documentation are not subject to the GNU General Public
License and may only be used or replicated with the express permission
of Red Hat, Inc.
"""

import json

import pytest

import tests
from mdapi.confdata import standard
from mdapi.services.main import buildapp


@pytest.fixture
@pytest.mark.usefixtures("setup_environment")
async def testing_application(setup_environment, event_loop, aiohttp_client):
    standard.DB_FOLDER = tests.LOCATION
    applobjc = await buildapp()
    return await aiohttp_client(applobjc)


@pytest.mark.download_required
async def test_view_index_page(testing_application):
    respobjc = await testing_application.get("/")
    assert respobjc.status == 200  # noqa : S101
    botmtext = "2015-2022 - Red Hat, Inc. - GPLv3+ - Sources:"
    otptrslt = await respobjc.text()
    assert botmtext in otptrslt  # noqa : S101


@pytest.mark.download_required
async def test_view_branches(testing_application):
    if False in [tests.databases_presence(indx) for indx in tests.PROBEURL.keys()]:
        pytest.xfail(reason="Databases are not available locally")
    else:
        respobjc = await testing_application.get("/branches")
        assert respobjc.status == 200  # noqa : S101
        otptobjc = await respobjc.text()
        assert "rawhide" in otptobjc  # noqa : S101
        assert "koji" in otptobjc  # noqa : S101


@pytest.mark.download_required
async def test_view_pkg_rawhide(testing_application):
    if not tests.databases_presence("rawhide"):
        pytest.xfail(reason="Databases for 'rawhide' repositories are not available locally")
    else:
        respobjc = await testing_application.get("/rawhide/pkg/kernel")
        assert respobjc.status == 200  # noqa : S101
        json.loads(await respobjc.text())


@pytest.mark.download_required
async def test_view_pkg_rawhide_invalid(testing_application):
    if not tests.databases_presence("rawhide"):
        pytest.xfail(reason="Databases for 'rawhide' repositories are not available locally")
    else:
        respobjc = await testing_application.get("/rawhide/pkg/invalidpackagename")
        assert respobjc.status == 404  # noqa : S101
        assert "404: Not Found" == await respobjc.text()  # noqa : S101


@pytest.mark.download_required
async def test_view_pkg_srcpkg_rawhide(testing_application):
    if not tests.databases_presence("rawhide"):
        pytest.xfail(reason="Databases for 'rawhide' repositories are not available locally")
    else:
        respobjc = await testing_application.get("/rawhide/srcpkg/python-natsort")
        assert respobjc.status == 200  # noqa : S101
        json.loads(await respobjc.text())  # noqa : S101


@pytest.mark.download_required
async def test_view_pkg_srcpkg_rawhide_subpackage_version(testing_application):
    if not tests.databases_presence("rawhide"):
        pytest.xfail(reason="Databases for 'rawhide' repositories are not available locally")
    else:
        respobjc = await testing_application.get("/rawhide/pkg/ruby")
        assert respobjc.status == 200  # noqa : S101
        pkgversion = json.loads(await respobjc.text())["version"]

        respobjc = await testing_application.get("/rawhide/srcpkg/ruby")
        assert respobjc.status == 200  # noqa : S101
        srcversion = json.loads(await respobjc.text())["version"]

        assert pkgversion == srcversion  # noqa : S101


@pytest.mark.download_required
async def test_view_changelog_rawhide(testing_application):
    if not tests.databases_presence("rawhide"):
        pytest.xfail(reason="Databases for 'rawhide' repositories are not available locally")
    else:
        respobjc = await testing_application.get("/rawhide/changelog/kernel")
        assert respobjc.status == 200  # noqa : S101
        json.loads(await respobjc.text())


@pytest.mark.download_required
@pytest.mark.parametrize(
    "action, package, status_code",
    [
        ("requires", "R", 200),
        ("provides", "perl(SetupLog)", 400),
        ("provides", "R", 200),
        ("obsoletes", "cabal2spec", 400),
        ("conflicts", "mariadb", 200),
        ("enhances", "httpd", 200),
        ("recommends", "flac", 200),
        ("suggests", "httpd", 200),
        ("supplements", "(hunspell and langpacks-fr)", 200),
    ],
)
async def test_view_property_koji(testing_application, action, package, status_code):
    if not tests.databases_presence("koji"):
        pytest.xfail(reason="Databases for 'koji' repositories are not available locally")
    else:
        respobjc = await testing_application.get(f"/koji/{action}/{package}")
        assert respobjc.status == status_code  # noqa : S101
        if status_code == 200:
            json.loads(await respobjc.text())  # noqa : S101
