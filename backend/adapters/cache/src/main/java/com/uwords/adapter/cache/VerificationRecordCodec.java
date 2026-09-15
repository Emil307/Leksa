package com.uwords.adapter.cache;

import com.uwords.domain.auth.challenge.ChallengeVerification;
import com.uwords.domain.common.UuidText;
import java.util.Map;

public final class VerificationRecordCodec {

    public static final String CHALLENGE_ID = "challengeId";
    public static final String USER_ID = "userId";
    public static final String SESSION_ID = "sessionId";

    private VerificationRecordCodec() {
    }

    public static String encode(ChallengeVerification verification) {
        StringBuilder record = new StringBuilder(FlatJson.OBJECT_START);
        appendText(record, CHALLENGE_ID, verification.challengeId().toString());
        record.append(FlatJson.FIELD_SEPARATOR);
        appendText(record, USER_ID, verification.userId().toString());
        record.append(FlatJson.FIELD_SEPARATOR);
        appendText(record, SESSION_ID, verification.sessionId().toString());
        return record.append(FlatJson.OBJECT_END).toString();
    }

    public static ChallengeVerification decode(String raw) {
        Map<String, String> fields = FlatJson.fields(raw);
        return new ChallengeVerification(
                UuidText.parse(fields.get(CHALLENGE_ID)).orElseThrow(),
                UuidText.parse(fields.get(USER_ID)).orElseThrow(),
                UuidText.parse(fields.get(SESSION_ID)).orElseThrow());
    }

    private static void appendText(StringBuilder record, String name, String value) {
        record.append(FlatJson.quoted(name)).append(FlatJson.NAME_SEPARATOR).append(FlatJson.quoted(value));
    }
}
