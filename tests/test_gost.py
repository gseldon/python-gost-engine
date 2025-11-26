#!/usr/bin/env python3
"""
Test suite for GOST cryptographic functionality
"""

import subprocess
import sys
import ssl


def test_python_ssl_module():
    """Test Python SSL module is available"""
    print("Testing Python SSL module...")
    try:
        version = ssl.OPENSSL_VERSION
        assert "OpenSSL 3" in version, f"Unexpected OpenSSL version: {version}"
        print(f"  ✓ SSL module available: {version}")
        return True
    except Exception as e:
        print(f"  ✗ SSL module test failed: {e}")
        return False


def test_gost_engine_loaded():
    """Test GOST engine is available in OpenSSL"""
    print("Testing GOST engine availability...")
    try:
        result = subprocess.run(
            ["openssl", "engine", "-t", "gost"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "available" in result.stdout:
            print(f"  ✓ GOST engine is available")
            return True
        else:
            print(f"  ✗ GOST engine not available: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ GOST engine test failed: {e}")
        return False


def test_gostsum_utility():
    """Test gostsum utility"""
    print("Testing gostsum utility...")
    try:
        result = subprocess.run(
            ["sh", "-c", "echo 'test data' | gostsum"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and len(result.stdout.strip()) > 0:
            print(f"  ✓ gostsum works: {result.stdout.strip()[:32]}...")
            return True
        else:
            print(f"  ✗ gostsum failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ gostsum test failed: {e}")
        return False


def test_gost12sum_utility():
    """Test gost12sum utility"""
    print("Testing gost12sum utility...")
    try:
        result = subprocess.run(
            ["sh", "-c", "echo 'test data' | gost12sum"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and len(result.stdout.strip()) > 0:
            print(f"  ✓ gost12sum works: {result.stdout.strip()[:32]}...")
            return True
        else:
            print(f"  ✗ gost12sum failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ gost12sum test failed: {e}")
        return False


def test_openssl_gost_digest():
    """Test OpenSSL GOST digest algorithms"""
    print("Testing OpenSSL GOST digest...")
    try:
        result = subprocess.run(
            ["sh", "-c", "echo 'test' | openssl dgst -engine gost -md_gost12_256"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and len(result.stdout) > 0:
            print(f"  ✓ GOST digest works")
            return True
        else:
            print(f"  ✗ GOST digest failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ GOST digest test failed: {e}")
        return False


def test_key_generation():
    """Test GOST key generation"""
    print("Testing GOST key generation...")
    try:
        result = subprocess.run(
            ["openssl", "genpkey", "-engine", "gost", "-algorithm", "gost2012_256", 
             "-pkeyopt", "paramset:A", "-out", "/tmp/test_key.pem"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✓ Key generation successful")
            return True
        else:
            print(f"  ✗ Key generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Key generation test failed: {e}")
        return False


def test_curl_availability():
    """Test curl is available for GOST site access"""
    print("Testing curl availability...")
    try:
        result = subprocess.run(
            ["curl", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"  ✓ curl available: {version}")
            return True
        else:
            print(f"  ✗ curl not available")
            return False
    except Exception as e:
        print(f"  ✗ curl test failed: {e}")
        return False


def test_python_packages():
    """Test required Python packages are installed"""
    print("Testing Python packages...")
    try:
        import requests
        import urllib3
        print(f"  ✓ requests {requests.__version__} installed")
        print(f"  ✓ urllib3 {urllib3.__version__} installed")
        return True
    except ImportError as e:
        print(f"  ✗ Package import failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("GOST Cryptographic Functionality Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_python_ssl_module,
        test_gost_engine_loaded,
        test_gostsum_utility,
        test_gost12sum_utility,
        test_openssl_gost_digest,
        test_key_generation,
        test_curl_availability,
        test_python_packages,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())




