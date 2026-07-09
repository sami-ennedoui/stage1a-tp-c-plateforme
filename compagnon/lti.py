"""Pont vers pylti1p3 : configuration de l'outil, JWKS, poussée AGS. Aucune route ici.
Toute la configuration vient des variables d'environnement, spec section 11."""
import os
from datetime import datetime, timezone

import requests
from pylti1p3.tool_config import ToolConfDict

DELAI_REQUETE_MOODLE = 15  # secondes


class _SessionBornee(requests.Session):
    """Session requests dont chaque appel porte un délai maximal : sans borne,
    un Moodle lent suspend la poussée indéfiniment, spec section 8."""

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", DELAI_REQUETE_MOODLE)
        return super().request(*args, **kwargs)


def conf_outil() -> ToolConfDict:
    iss = os.environ["MOODLE_ISS"]
    client_id = os.environ["MOODLE_CLIENT_ID"]
    conf = ToolConfDict({iss: [{
        "default": True,
        "client_id": client_id,
        "auth_login_url": os.environ["MOODLE_AUTH_LOGIN_URL"],
        "auth_token_url": os.environ["MOODLE_AUTH_TOKEN_URL"],
        "key_set_url": os.environ["MOODLE_KEY_SET_URL"],
        "deployment_ids": [os.environ["MOODLE_DEPLOYMENT_ID"]],
    }]})
    conf.set_private_key(iss, os.environ["TOOL_PRIVATE_KEY"], client_id=client_id)
    conf.set_public_key(iss, os.environ["TOOL_PUBLIC_KEY"], client_id=client_id)
    return conf


def jwks() -> dict:
    return conf_outil().get_jwks()


def pousser_score(sub: str, valeur: float, ags_claim: dict) -> None:
    """Écrit un score au carnet par AGS, hors de tout lancement, spec section 5.
    Lève une exception réseau ou pylti1p3 si Moodle ne répond pas, l'appelant décide."""
    from pylti1p3.assignments_grades import AssignmentsGradesService
    from pylti1p3.grade import Grade
    from pylti1p3.service_connector import ServiceConnector

    conf = conf_outil()
    registration = conf.find_registration_by_issuer(os.environ["MOODLE_ISS"])
    connecteur = ServiceConnector(registration, requests_session=_SessionBornee())
    service = AssignmentsGradesService(connecteur, ags_claim)
    note = (Grade()
            .set_score_given(valeur)
            .set_score_maximum(100)
            .set_activity_progress("Completed")
            .set_grading_progress("FullyGraded")
            .set_timestamp(datetime.now(timezone.utc).isoformat())
            .set_user_id(sub))
    service.put_grade(note)
