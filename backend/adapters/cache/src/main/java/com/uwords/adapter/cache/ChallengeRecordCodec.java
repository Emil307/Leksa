package com.uwords.adapter.cache;

import com.uwords.domain.auth.challenge.Challenge;
import com.uwords.domain.auth.challenge.ChallengeType;
import com.uwords.domain.common.UuidText;
import com.uwords.usecase.port.auth.challenge.StoredChallenge;
import java.util.Map;

public final class ChallengeRecordCodec {

    public static final String ID = "id";
    public static final String CHALLENGE_TYPE = "challengeType";
    public static final String UNIQUENESS_KEY = "uniquenessKey";
    public static final String SECRET = "secret";
    public static final String CREATED_AT = "createdAt";
    public static final String EXPIRES_AT = "expiresAt";
    public static final String ATTEMPTS = "attempts";

    private ChallengeRecordCodec() {
    }

    public static String encode(Challenge challenge) {
        StringBuilder record = new StringBuilder(FlatJson.OBJECT_START);
        appendText(record, ID, challenge.id().toString());
        record.append(FlatJson.FIELD_SEPARATOR);
        appendText(record, CHALLENGE_TYPE, challenge.challengeType().value());
        record.append(FlatJson.FIELD_SEPARATOR);
        appendText(record, UNIQUENESS_KEY, challenge.uniquenessKey());
        record.append(FlatJson.FIELD_SEPARATOR);
        appendText(record, SECRET, challenge.secretValue());
        record.append(FlatJson.FIELD_SEPARATOR);
        appendText(record, CREATED_AT, IsoOffsetText.of(challenge.createdAt()));
        record.append(FlatJson.FIELD_SEPARATOR);
        appendText(record, EXPIRES_AT, IsoOffsetText.of(challenge.expiresAt()));
        record.append(FlatJson.FIELD_SEPARATOR);
        record.append(FlatJson.quoted(ATTEMPTS)).append(FlatJson.NAME_SEPARATOR).append(challenge.attempts());
        return record.append(FlatJson.OBJECT_END).toString();
    }

    public static StoredChallenge decode(String raw) {
        Map<String, String> fields = FlatJson.fields(raw);
        return new StoredChallenge(
                UuidText.parse(fields.get(ID)).orElseThrow(),
                ChallengeType.from(fields.get(CHALLENGE_TYPE)),
                fields.get(UNIQUENESS_KEY),
                fields.get(SECRET),
                IsoOffsetText.parse(fields.get(CREATED_AT)),
                IsoOffsetText.parse(fields.get(EXPIRES_AT)),
                Integer.parseInt(fields.get(ATTEMPTS).strip()));
    }

    private static void appendText(StringBuilder record, String name, String value) {
        record.append(FlatJson.quoted(name)).append(FlatJson.NAME_SEPARATOR).append(FlatJson.quoted(value));
    }
}
