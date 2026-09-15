package com.uwords.usecase.service.auth;

import com.uwords.domain.auth.session.RefreshToken;
import com.uwords.usecase.port.auth.session.IssuedSessionRecord;

record IssuedSessionTokens(IssuedSessionRecord issued, RefreshToken refreshToken) {
}
