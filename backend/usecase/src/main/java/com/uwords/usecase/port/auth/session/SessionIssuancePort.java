package com.uwords.usecase.port.auth.session;

public interface SessionIssuancePort {

    IssuedSessionRecord issueSession(SessionIssuanceRequest request);
}
