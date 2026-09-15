package com.uwords.usecase.port.auth.session;

import com.uwords.domain.auth.session.AccessTokenClaims;

public interface AccessTokenIssuerPort {

    String issue(AccessTokenClaims claims);
}
