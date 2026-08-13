from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile

from app.services import farmer_service, land_service


@pytest.mark.parametrize(
    ("service", "directory_attribute", "save_function"),
    [
        (farmer_service, "FARMER_PHOTO_DIR", farmer_service.save_farmer_photo),
        (land_service, "LAND_PHOTO_DIR", land_service.save_land_photo),
    ],
)
def test_photo_larger_than_five_mb_is_rejected_and_removed(
    tmp_path, monkeypatch, service, directory_attribute, save_function
):
    photo_directory = tmp_path / "photos"
    monkeypatch.setattr(service, directory_attribute, photo_directory)
    photo = UploadFile(
        filename="large.jpg",
        file=BytesIO(b"x" * (service.MAX_PHOTO_SIZE + 1)),
        headers={"content-type": "image/jpeg"},
    )

    with pytest.raises(HTTPException) as error:
        save_function(photo)

    assert error.value.status_code == 413
    assert error.value.detail == "Ukuran foto maksimal 5 MB"
    assert list(photo_directory.iterdir()) == []


@pytest.mark.parametrize(
    ("service", "directory_attribute", "save_function"),
    [
        (farmer_service, "FARMER_PHOTO_DIR", farmer_service.save_farmer_photo),
        (land_service, "LAND_PHOTO_DIR", land_service.save_land_photo),
    ],
)
def test_photo_exactly_five_mb_is_accepted(
    tmp_path, monkeypatch, service, directory_attribute, save_function
):
    photo_directory = tmp_path / "photos"
    monkeypatch.setattr(service, directory_attribute, photo_directory)
    photo = UploadFile(
        filename="allowed.jpg",
        file=BytesIO(b"x" * service.MAX_PHOTO_SIZE),
        headers={"content-type": "image/jpeg"},
    )

    saved_path = save_function(photo)

    saved_file = photo_directory / Path(saved_path).name
    assert saved_file.stat().st_size == service.MAX_PHOTO_SIZE
