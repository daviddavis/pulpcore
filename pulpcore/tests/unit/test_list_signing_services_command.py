import pytest
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

from pulpcore.app.models.content import SigningService, AsciiArmoredDetachedSigningService


@pytest.mark.django_db
def test_list_signing_services_empty():
    """Test the list-signing-services command with no signing services."""
    out = StringIO()
    call_command("list-signing-services", stdout=out)
    assert out.getvalue().strip() == ""


@pytest.mark.django_db
def test_list_signing_services_single(tmp_path):
    """Test the list-signing-services command with a single signing service."""
    # Create a dummy script file
    script_file = tmp_path / "signing_script.sh"
    script_file.write_text("#!/bin/bash\necho 'test'")
    
    # Create a signing service with mocked validate() method
    service = AsciiArmoredDetachedSigningService(
        name="test-service",
        public_key="test-key",
        pubkey_fingerprint="test-fingerprint",
        script=str(script_file),
    )
    # Mock the validate method to bypass GPG verification
    with patch.object(service, 'validate', return_value=None):
        service.save()
    
    out = StringIO()
    call_command("list-signing-services", stdout=out)
    output = out.getvalue().strip()
    assert output == "test-service"


@pytest.mark.django_db
def test_list_signing_services_multiple(tmp_path):
    """Test the list-signing-services command with multiple signing services."""
    # Create a dummy script file
    script_file = tmp_path / "signing_script.sh"
    script_file.write_text("#!/bin/bash\necho 'test'")
    
    # Create multiple signing services with mocked validate() method
    for name in ["service-a", "service-b", "service-c"]:
        service = AsciiArmoredDetachedSigningService(
            name=name,
            public_key=f"key-{name[-1]}",
            pubkey_fingerprint=f"fingerprint-{name[-1]}",
            script=str(script_file),
        )
        # Mock the validate method to bypass GPG verification
        with patch.object(service, 'validate', return_value=None):
            service.save()
    
    out = StringIO()
    call_command("list-signing-services", stdout=out)
    output_lines = out.getvalue().strip().split("\n")
    
    # Check that all service names are present
    assert "service-a" in output_lines
    assert "service-b" in output_lines
    assert "service-c" in output_lines
