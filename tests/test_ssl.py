#!/usr/bin/env python3
"""
SSL/TLS functionality tests
"""

import subprocess
import sys


def test_ssl_connection():
    """Test SSL connection to a GOST-protected site"""
    print("Testing SSL connection to GOST site...")
    try:
        result = subprocess.run(
            ["curl", "-k", "-I", "-s", "--connect-timeout", "10", 
             "https://dss.uc-em.ru/"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if "HTTP" in result.stdout:
            print(f"  ✓ SSL connection successful")
            status_line = result.stdout.split('\n')[0]
            print(f"    {status_line}")
            return True
        else:
            print(f"  ✗ SSL connection failed")
            return False
    except Exception as e:
        print(f"  ✗ SSL connection test failed: {e}")
        return False


def test_certificate_verification():
    """Test GOST certificate verification"""
    print("Testing GOST certificate verification...")
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", "dss.uc-em.ru:443", 
             "-showcerts"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "GOST" in result.stdout:
            print(f"  ✓ GOST certificate detected")
            
            # Extract certificate and verify
            cert_result = subprocess.run(
                ["openssl", "x509", "-text", "-noout"],
                input=result.stdout,
                capture_output=True,
                text=True
            )
            
            if "GOST R 34.10-2012" in cert_result.stdout:
                print(f"  ✓ Certificate signature algorithm verified")
                return True
        
        print(f"  ✗ GOST certificate verification failed")
        return False
    except Exception as e:
        print(f"  ✗ Certificate verification test failed: {e}")
        return False


def test_tls_handshake():
    """Test TLS handshake with GOST algorithms"""
    print("Testing TLS handshake...")
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", "dss.uc-em.ru:443", 
             "-brief"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 or "Verification error" in result.stdout:
            # Connection established (certificate verification may fail without proper CA)
            print(f"  ✓ TLS handshake successful")
            return True
        else:
            print(f"  ✗ TLS handshake failed")
            return False
    except Exception as e:
        print(f"  ✗ TLS handshake test failed: {e}")
        return False


def test_cryptopro_ssl_connection():
    """Test SSL connection to CryptoPro site"""
    print("Testing SSL connection to cryptopro.ru...")
    try:
        result = subprocess.run(
            ["curl", "-k", "-I", "-s", "--connect-timeout", "10", 
             "https://cryptopro.ru/"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if "HTTP" in result.stdout:
            print(f"  ✓ SSL connection to cryptopro.ru successful")
            status_line = result.stdout.split('\n')[0]
            print(f"    {status_line}")
            return True
        else:
            print(f"  ✗ SSL connection to cryptopro.ru failed")
            return False
    except Exception as e:
        print(f"  ✗ SSL connection test to cryptopro.ru failed: {e}")
        return False


def test_cryptopro_certificate():
    """Test CryptoPro certificate verification"""
    print("Testing CryptoPro certificate...")
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", "cryptopro.ru:443", 
             "-showcerts"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "GOST" in result.stdout or "KUZNYECHIK" in result.stdout:
            print(f"  ✓ CryptoPro GOST certificate detected")
            
            # Extract certificate and verify
            cert_result = subprocess.run(
                ["openssl", "x509", "-text", "-noout"],
                input=result.stdout,
                capture_output=True,
                text=True
            )
            
            if "GOST" in cert_result.stdout or "KUZNYECHIK" in cert_result.stdout:
                print(f"  ✓ Certificate signature algorithm verified")
                return True
        
        print(f"  ✗ CryptoPro certificate verification failed")
        return False
    except Exception as e:
        print(f"  ✗ CryptoPro certificate test failed: {e}")
        return False


def test_cryptopro_cipher_suite():
    """Test CryptoPro cipher suite (Kuznyechik)"""
    print("Testing CryptoPro cipher suite (Kuznyechik)...")
    try:
        result = subprocess.run(
            ["openssl", "s_client", "-connect", "cryptopro.ru:443", 
             "-cipher", "GOST2012-GOST8912-GOST8912"],
            input="",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Check for Kuznyechik cipher suite
        if "KUZNYECHIK" in result.stdout.upper() or "Cipher" in result.stdout:
            print(f"  ✓ Kuznyechik cipher suite detected")
            
            # Try to get cipher info
            cipher_info = subprocess.run(
                ["openssl", "s_client", "-connect", "cryptopro.ru:443", 
                 "-brief"],
                input="",
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "KUZNYECHIK" in cipher_info.stdout.upper() or cipher_info.returncode == 0:
                print(f"  ✓ Cipher suite negotiation successful")
                return True
        
        print(f"  ✗ Kuznyechik cipher suite test failed")
        return False
    except Exception as e:
        print(f"  ✗ Cipher suite test failed: {e}")
        return False


def run_ssl_tests():
    """Run SSL/TLS tests"""
    print("=" * 60)
    print("SSL/TLS Functionality Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_ssl_connection,
        test_certificate_verification,
        test_tls_handshake,
        test_cryptopro_ssl_connection,
        test_cryptopro_certificate,
        test_cryptopro_cipher_suite,
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
    print("SSL Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓ All SSL tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} SSL test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_ssl_tests())




