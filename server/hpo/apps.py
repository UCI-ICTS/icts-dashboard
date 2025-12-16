#!/usr/bin/env python
# hpo/apps.py


from django.apps import AppConfig
import logging

log = logging.getLogger(__name__)

class HpoConfig(AppConfig):
    name = "hpo"
    default_auto_field = "django.db.models.BigAutoField"
    # def ready(self):
    #     from hpo.services import get_active_artifact
    #     art = get_active_artifact()
    #     if not art:
    #         log.warning("[HPO] No active artifact found.")
    #         return

    #     if not art.faiss_path or not art.npz_path:
    #         log.warning(
    #             f"[HPO] Active artifact '{art.release}' missing FAISS/NPZ paths. "
    #             "Search will fail until build_vectors_from_csv() is run."
    #         )
    #     else:
    #         log.info(
    #             f"[HPO] Active artifact: release={art.release}, "
    #             f"faiss='{art.faiss_path}', npz='{art.npz_path}'"
    #         )
