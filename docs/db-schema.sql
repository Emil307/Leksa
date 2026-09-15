CREATE SCHEMA "auth";

CREATE SCHEMA "billing";

CREATE SCHEMA "dictionary";

CREATE SCHEMA "learner";

CREATE SCHEMA "analysis";

CREATE SCHEMA "media";

CREATE SCHEMA "notifications";

CREATE TYPE "auth"."provider_enum" AS ENUM (
  'google',
  'email',
  'telegram'
);

CREATE TYPE "auth"."user_gender" AS ENUM (
  'male',
  'female'
);

CREATE TYPE "billing"."payment_provider_enum" AS ENUM (
  'yookassa',
  'stripe'
);

CREATE TYPE "dictionary"."language_enum" AS ENUM (
  'ru',
  'en'
);

CREATE TYPE "dictionary"."word_source_enum" AS ENUM (
  'TEAM',
  'TRANSLATOR',
  'SEARCH',
  'ANALYZER',
  'SYNONYM_GENERATION'
);

CREATE TYPE "learner"."language_enum" AS ENUM (
  'ru',
  'en'
);

CREATE TYPE "learner"."strike_status_enum" AS ENUM (
  'COMPLETED',
  'UNCOMPLETED'
);

CREATE TYPE "analysis"."job_type_enum" AS ENUM (
  'SPEECH_ANALYSIS'
);

CREATE TYPE "analysis"."job_status_enum" AS ENUM (
  'PENDING',
  'PROCESSING',
  'COMPLETED',
  'FAILED',
  'PROCESSED_BY_USER'
);

CREATE TYPE "notifications"."outbox_type_enum" AS ENUM (
  'SendEmailCode'
);

CREATE TYPE "notifications"."outbox_status_enum" AS ENUM (
  'ACTIVE',
  'PROCESS',
  'COMPLETED',
  'FAILED'
);

CREATE TABLE "auth"."t_users" (
  "id" uuid PRIMARY KEY,
  "name" varchar NOT NULL,
  "surname" varchar,
  "email" varchar UNIQUE,
  "is_superuser" boolean DEFAULT false,
  "created_at" timestamptz,
  "updated_at" timestamptz,
  "avatar_id" uuid,
  "birthday" date,
  "gender" auth.user_gender,
  "city" varchar,
  "phone" varchar
);

CREATE TABLE "auth"."t_auth" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "provider" auth.provider_enum NOT NULL,
  "provider_id" varchar UNIQUE NOT NULL,
  "created_at" timestamptz
);

CREATE TABLE "auth"."t_sessions" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "refresh_token" varchar NOT NULL,
  "created_at" timestamptz
);

CREATE TABLE "billing"."t_customers" (
  "user_id" uuid PRIMARY KEY,
  "stripe_customer_id" varchar UNIQUE
);

CREATE TABLE "billing"."t_subscriptions" (
  "id" uuid PRIMARY KEY,
  "plan_name" varchar NOT NULL,
  "period" integer NOT NULL,
  "cost" float NOT NULL,
  "cost_usd" float,
  "active" boolean DEFAULT true,
  "stripe_price_id" varchar UNIQUE,
  "extra_info" json
);

CREATE TABLE "billing"."t_user_subscriptions" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "subscription_id" uuid NOT NULL,
  "subscribed_from" timestamptz,
  "subscribed_until" timestamptz,
  "trial_from" timestamptz,
  "trial_until" timestamptz,
  "used_free_trial" boolean DEFAULT false,
  "payment_id" varchar,
  "payment_provider" billing.payment_provider_enum,
  "confirmed" boolean,
  "is_cancelled" boolean DEFAULT false,
  "speech_analysis_day_usage" integer DEFAULT 0
);

CREATE TABLE "dictionary"."t_words" (
  "id" uuid PRIMARY KEY,
  "picture_id" uuid,
  "is_special_word" boolean NOT NULL DEFAULT false,
  "is_similar" boolean NOT NULL DEFAULT false,
  "created_at" timestamptz
);

CREATE TABLE "dictionary"."t_translations" (
  "id" uuid PRIMARY KEY,
  "word_id" uuid NOT NULL,
  "parent_id" uuid NOT NULL,
  "language" dictionary.language_enum NOT NULL,
  "translation" varchar NOT NULL,
  "transcription" varchar,
  "meaning" varchar,
  "pos" varchar,
  "form" varchar,
  "complexity" integer,
  "source" dictionary.word_source_enum NOT NULL,
  "description" varchar,
  "is_active" boolean DEFAULT true,
  "audio_id" uuid
);

CREATE TABLE "dictionary"."t_examples" (
  "id" uuid PRIMARY KEY,
  "translation_id" uuid NOT NULL,
  "text" varchar NOT NULL
);

CREATE TABLE "learner"."t_profiles" (
  "user_id" uuid PRIMARY KEY,
  "initial_language" learner.language_enum NOT NULL,
  "target_language" learner.language_enum NOT NULL,
  "experience" integer DEFAULT 0,
  "study_time" integer DEFAULT 5,
  "proficiency_level" integer DEFAULT 0,
  "level" integer DEFAULT 1
);

CREATE TABLE "learner"."t_onboarding" (
  "user_id" uuid PRIMARY KEY,
  "analysis_onboarding_completed" boolean DEFAULT false,
  "full_onboarding_completed" boolean DEFAULT false,
  "is_profile_onboarding_completed" boolean DEFAULT false,
  "is_translator_onboarding_completed" boolean DEFAULT false,
  "is_games_onboarding_completed" boolean DEFAULT false,
  "is_myvawe_onboarding_completed" boolean DEFAULT false,
  "is_synonimyzer_onboarding_completed" boolean DEFAULT false,
  "is_scribe_onboarding_completed" boolean DEFAULT false,
  "is_wordsmania_onboarding_completed" boolean DEFAULT false,
  "is_training_onboarding_completed" boolean DEFAULT false,
  "is_dictionary_onboarding_completed" boolean DEFAULT false
);

CREATE TABLE "learner"."t_user_words" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "word_id" uuid NOT NULL,
  "is_favorite" boolean DEFAULT false,
  "added_at" timestamptz,
  "last_mistaken" timestamptz,
  "num_mistakes" integer DEFAULT 0,
  "num_trainings_passed" integer DEFAULT 0,
  "from_translator" boolean DEFAULT false
);

CREATE TABLE "learner"."t_strikes" (
  "user_id" uuid NOT NULL,
  "date" date NOT NULL,
  "status" learner.strike_status_enum NOT NULL DEFAULT 'UNCOMPLETED',
  "xp" integer DEFAULT 0,
  PRIMARY KEY ("user_id", "date")
);

CREATE TABLE "learner"."t_user_games" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "my_wave_count" integer DEFAULT 0,
  "picez_count" integer DEFAULT 0,
  "synonimizator_count" integer DEFAULT 0,
  "slovomania_count" integer DEFAULT 0,
  "training_count" integer DEFAULT 0
);

CREATE TABLE "learner"."t_reviews" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "score" integer DEFAULT 0,
  "comment" varchar DEFAULT '',
  "created_at" timestamptz
);

CREATE TABLE "learner"."t_proficiency_levels" (
  "level" integer,
  "language" language_enum,
  "label" varchar(200),
  CONSTRAINT "chk_prof_level" CHECK (level >= 0 and level <= 100),
  PRIMARY KEY ("level", "language")
);

CREATE TABLE "analysis"."t_jobs" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "type" analysis.job_type_enum NOT NULL,
  "status" analysis.job_status_enum NOT NULL DEFAULT 'PENDING',
  "job_data" json,
  "job_result" json,
  "timeout" timestamptz,
  "created_at" timestamptz
);

CREATE TABLE "media"."t_assets" (
  "id" uuid PRIMARY KEY,
  "url" varchar NOT NULL,
  "content_type" varchar NOT NULL,
  "alt" varchar,
  "type" varchar NOT NULL DEFAULT 'BASE'
);

CREATE TABLE "notifications"."t_outbox" (
  "id" uuid PRIMARY KEY,
  "type" notifications.outbox_type_enum NOT NULL,
  "status" notifications.outbox_status_enum NOT NULL DEFAULT 'ACTIVE',
  "data" jsonb NOT NULL,
  "attempts" integer NOT NULL DEFAULT 0,
  "last_error" varchar,
  "created_at" timestamptz NOT NULL DEFAULT now(),
  "updated_at" timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON "auth"."t_sessions" ("user_id");

CREATE INDEX ON "notifications"."t_outbox" ("status", "created_at");

CREATE UNIQUE INDEX ON "dictionary"."t_translations" ("word_id", "language");

CREATE UNIQUE INDEX ON "learner"."t_user_words" ("user_id", "word_id");

COMMENT ON COLUMN "auth"."t_users"."avatar_id" IS '→ media.t_assets.id';

COMMENT ON COLUMN "billing"."t_customers"."user_id" IS '→ auth.t_users.id';

COMMENT ON COLUMN "billing"."t_user_subscriptions"."user_id" IS '→ auth.t_users.id';

COMMENT ON COLUMN "dictionary"."t_words"."picture_id" IS '→ media.t_assets.id';

COMMENT ON TABLE "dictionary"."t_translations" IS 'CHECK: complexity 1..100';

COMMENT ON COLUMN "dictionary"."t_translations"."complexity" IS 'сложность переведенного слова';

COMMENT ON COLUMN "dictionary"."t_translations"."audio_id" IS '→ media.t_assets.id';

COMMENT ON TABLE "learner"."t_profiles" IS 'CHECK: study_time 5..1439, proficiency_level 0..100';

COMMENT ON COLUMN "learner"."t_profiles"."user_id" IS '→ auth.t_users.id';

COMMENT ON COLUMN "learner"."t_profiles"."experience" IS 'общий опыт в приложении';

COMMENT ON COLUMN "learner"."t_profiles"."study_time" IS 'на его основе рассчитывается требуемый темп обучения и колво xp в день чтобы закрыть strike';

COMMENT ON COLUMN "learner"."t_profiles"."proficiency_level" IS 'уровень владения целевого языка. Рассчитывается на этапе онбординга и меняется по мере использования приложения через таблицу proficiency_levels';

COMMENT ON COLUMN "learner"."t_profiles"."level" IS 'уровень внутри приложения';

COMMENT ON COLUMN "learner"."t_user_words"."word_id" IS '→ dictionary.t_words.id';

COMMENT ON COLUMN "learner"."t_proficiency_levels"."level" IS 'уровень владения языка / сложности слова в расчете по 100 бальной шкале';

COMMENT ON COLUMN "learner"."t_proficiency_levels"."label" IS 'описание конкретного уровня, например ''intermediate'' для английского';

COMMENT ON COLUMN "analysis"."t_jobs"."user_id" IS '→ auth.t_users.id';

ALTER TABLE "auth"."t_auth" ADD FOREIGN KEY ("user_id") REFERENCES "auth"."t_users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "auth"."t_sessions" ADD FOREIGN KEY ("user_id") REFERENCES "auth"."t_users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "billing"."t_user_subscriptions" ADD FOREIGN KEY ("subscription_id") REFERENCES "billing"."t_subscriptions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "dictionary"."t_translations" ADD FOREIGN KEY ("word_id") REFERENCES "dictionary"."t_words" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "dictionary"."t_translations" ADD FOREIGN KEY ("parent_id") REFERENCES "dictionary"."t_translations" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "dictionary"."t_examples" ADD FOREIGN KEY ("translation_id") REFERENCES "dictionary"."t_translations" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "learner"."t_profiles" ADD FOREIGN KEY ("user_id") REFERENCES "learner"."t_onboarding" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "learner"."t_user_words" ADD FOREIGN KEY ("user_id") REFERENCES "learner"."t_profiles" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "learner"."t_strikes" ADD FOREIGN KEY ("user_id") REFERENCES "learner"."t_profiles" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "learner"."t_user_games" ADD FOREIGN KEY ("user_id") REFERENCES "learner"."t_profiles" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "learner"."t_reviews" ADD FOREIGN KEY ("user_id") REFERENCES "learner"."t_profiles" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "learner"."t_profiles" ADD FOREIGN KEY ("target_language", "proficiency_level") REFERENCES "learner"."t_proficiency_levels" ("language", "level") DEFERRABLE INITIALLY IMMEDIATE;
