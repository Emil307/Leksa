package com.uwords.domain.auth.challenge;

import com.uwords.domain.auth.user.ProviderAccount;
import com.uwords.domain.notifications.OutboundNotification;

public interface ChallengeStrategy {

    ChallengeType challengeType();

    ChallengeSubject subjectOf(String credential);

    ChallengeSecret issueSecret();

    OutboundNotification notificationFor(Challenge challenge, ChallengeSubject subject);

    ChallengeSecret restoreSecret(String value);

    ProviderAccount accountFor(String uniquenessKey);
}
