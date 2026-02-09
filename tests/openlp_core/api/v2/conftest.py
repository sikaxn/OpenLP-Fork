import pytest

from openlp.core.api import app as flask_app


@pytest.fixture(scope='module')
def flask_client():
    flask_app.config['TESTING'] = True
    return flask_app.test_client()
