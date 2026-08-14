export function validateTotpSecret(value) {
  if (!value) {
    return { ok: true, normalized: '' }
  }

  const sanitized = String(value).trim().replace(/\s+/g, '').toUpperCase()

  if (/^\d{6,8}$/.test(sanitized)) {
    return {
      ok: false,
      message: 'You entered a 6-digit TOTP passcode instead of the 2FA Seed Key. Please paste the Base32 Secret Key.',
    }
  }

  const unpadded = sanitized.replace(/=+$/, '')
  if (!unpadded || !/^[A-Z2-7]+$/.test(unpadded) || unpadded.length < 8) {
    return {
      ok: false,
      message: 'Invalid TOTP Secret Key. Base32 keys must contain letters A-Z and digits 2-7 (at least 8 characters).',
    }
  }

  const remainder = unpadded.length % 8
  if ([1, 3, 6].includes(remainder)) {
    return {
      ok: false,
      message: 'Invalid Base32 TOTP Secret key length.',
    }
  }

  if (sanitized.includes('=')) {
    const expectedPadMap = { 0: 0, 2: 6, 4: 4, 5: 3, 7: 1 }
    const expectedPadLen = expectedPadMap[remainder] ?? 0
    const actualPadLen = sanitized.length - unpadded.length

    if (actualPadLen !== expectedPadLen) {
      return {
        ok: false,
        message: `Incorrect Base32 padding. Found ${actualPadLen} equal sign(s), expected ${expectedPadLen}.`,
      }
    }
  }

  return { ok: true, normalized: sanitized }
}
