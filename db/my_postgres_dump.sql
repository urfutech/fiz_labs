--
-- PostgreSQL database dump
--

\restrict TPPLP9RFVJzdKMxDQ4G0jGUZNpuchaDhoe9CN6UduR6YwWcx1waAdjIImEgdSDy

-- Dumped from database version 16.15 (Debian 16.15-1.pgdg13+2)
-- Dumped by pg_dump version 16.15 (Debian 16.15-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: admin
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO admin;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: admin
--

COMMENT ON SCHEMA public IS '';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: set_updated_at(); Type: FUNCTION; Schema: public; Owner: admin
--

CREATE FUNCTION public.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.set_updated_at() OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    actor_id integer,
    action character varying(64) NOT NULL,
    entity character varying(64) NOT NULL,
    entity_id integer,
    payload_json jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_log OWNER TO admin;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.audit_log ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.audit_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: groups; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.groups (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.groups OWNER TO admin;

--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.groups ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: lab_fields; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lab_fields (
    id integer NOT NULL,
    lab_id integer NOT NULL,
    field_key character varying(128) NOT NULL,
    label character varying(255) NOT NULL,
    field_type character varying(16) DEFAULT 'text'::character varying NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    required boolean DEFAULT true NOT NULL,
    CONSTRAINT lab_fields_type_chk CHECK (((field_type)::text = ANY ((ARRAY['text'::character varying, 'number'::character varying, 'table'::character varying, 'file'::character varying])::text[])))
);


ALTER TABLE public.lab_fields OWNER TO admin;

--
-- Name: lab_fields_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.lab_fields ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.lab_fields_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: lab_reports; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lab_reports (
    id integer NOT NULL,
    student_id integer NOT NULL,
    lab_id integer NOT NULL,
    status character varying(16) DEFAULT 'draft'::character varying NOT NULL,
    grade numeric(5,2),
    graded_by integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT lab_reports_grade_chk CHECK (((grade IS NULL) OR ((grade >= (0)::numeric) AND (grade <= (100)::numeric)))),
    CONSTRAINT lab_reports_grade_status_chk CHECK (((grade IS NULL) OR ((status)::text = 'graded'::text))),
    CONSTRAINT lab_reports_status_chk CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'submitted'::character varying, 'returned'::character varying, 'graded'::character varying])::text[])))
);


ALTER TABLE public.lab_reports OWNER TO admin;

--
-- Name: lab_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.lab_reports ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.lab_reports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: labs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.labs (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    is_published boolean DEFAULT false NOT NULL,
    created_by integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.labs OWNER TO admin;

--
-- Name: labs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.labs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.labs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ml_runs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.ml_runs (
    id integer NOT NULL,
    report_id integer NOT NULL,
    model_name character varying(128) NOT NULL,
    status character varying(16) DEFAULT 'pending'::character varying NOT NULL,
    result_json jsonb,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    CONSTRAINT ml_status_chk CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'running'::character varying, 'done'::character varying, 'failed'::character varying])::text[])))
);


ALTER TABLE public.ml_runs OWNER TO admin;

--
-- Name: ml_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.ml_runs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.ml_runs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: report_attachments; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.report_attachments (
    id integer NOT NULL,
    report_id integer NOT NULL,
    file_name character varying(255) NOT NULL,
    file_path character varying(512) NOT NULL,
    mime_type character varying(128),
    size_bytes bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT report_attachments_size_bytes_check CHECK ((size_bytes >= 0))
);


ALTER TABLE public.report_attachments OWNER TO admin;

--
-- Name: report_attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.report_attachments ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.report_attachments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: report_field_errors; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.report_field_errors (
    id integer NOT NULL,
    value_id integer NOT NULL,
    error_type character varying(32) NOT NULL,
    message text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.report_field_errors OWNER TO admin;

--
-- Name: report_field_errors_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.report_field_errors ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.report_field_errors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: report_field_values; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.report_field_values (
    id integer NOT NULL,
    report_id integer NOT NULL,
    field_id integer NOT NULL,
    value text,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.report_field_values OWNER TO admin;

--
-- Name: report_field_values_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.report_field_values ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.report_field_values_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: report_status_history; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.report_status_history (
    id integer NOT NULL,
    report_id integer NOT NULL,
    status character varying(16) NOT NULL,
    changed_by integer,
    comment text,
    changed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT rsh_status_chk CHECK (((status)::text = ANY ((ARRAY['draft'::character varying, 'submitted'::character varying, 'returned'::character varying, 'graded'::character varying])::text[])))
);


ALTER TABLE public.report_status_history OWNER TO admin;

--
-- Name: report_status_history_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.report_status_history ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.report_status_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: teacher_comments; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.teacher_comments (
    id integer NOT NULL,
    report_id integer NOT NULL,
    field_id integer,
    teacher_id integer NOT NULL,
    text text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.teacher_comments OWNER TO admin;

--
-- Name: teacher_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.teacher_comments ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.teacher_comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: teacher_groups; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.teacher_groups (
    teacher_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.teacher_groups OWNER TO admin;

--
-- Name: teacher_overrides; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.teacher_overrides (
    id integer NOT NULL,
    report_id integer NOT NULL,
    field_id integer NOT NULL,
    teacher_id integer NOT NULL,
    override_type character varying(16) NOT NULL,
    old_value text,
    new_value text,
    reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT to_type_chk CHECK (((override_type)::text = ANY ((ARRAY['accept'::character varying, 'correct'::character varying, 'reject'::character varying])::text[])))
);


ALTER TABLE public.teacher_overrides OWNER TO admin;

--
-- Name: teacher_overrides_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.teacher_overrides ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.teacher_overrides_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    role character varying(16) NOT NULL,
    login character varying(128) NOT NULL,
    password_hash character varying(255) NOT NULL,
    last_name character varying(64) NOT NULL,
    first_name character varying(64) NOT NULL,
    middle_name character varying(64),
    group_id integer,
    selectable_for_students boolean DEFAULT false NOT NULL,
    status character varying(16) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT users_group_chk CHECK ((((role)::text = 'student'::text) OR (group_id IS NULL))),
    CONSTRAINT users_role_chk CHECK (((role)::text = ANY ((ARRAY['admin'::character varying, 'moderator'::character varying, 'teacher'::character varying, 'student'::character varying])::text[]))),
    CONSTRAINT users_selectable_chk CHECK ((((role)::text = 'teacher'::text) OR (selectable_for_students = false))),
    CONSTRAINT users_status_chk CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'blocked'::character varying, 'archived'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.audit_log (id, actor_id, action, entity, entity_id, payload_json, created_at) FROM stdin;
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.groups (id, name, created_at) FROM stdin;
\.


--
-- Data for Name: lab_fields; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lab_fields (id, lab_id, field_key, label, field_type, "position", required) FROM stdin;
\.


--
-- Data for Name: lab_reports; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lab_reports (id, student_id, lab_id, status, grade, graded_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: labs; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.labs (id, title, description, is_published, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: ml_runs; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.ml_runs (id, report_id, model_name, status, result_json, started_at, finished_at) FROM stdin;
\.


--
-- Data for Name: report_attachments; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.report_attachments (id, report_id, file_name, file_path, mime_type, size_bytes, created_at) FROM stdin;
\.


--
-- Data for Name: report_field_errors; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.report_field_errors (id, value_id, error_type, message, created_at) FROM stdin;
\.


--
-- Data for Name: report_field_values; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.report_field_values (id, report_id, field_id, value, updated_at) FROM stdin;
\.


--
-- Data for Name: report_status_history; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.report_status_history (id, report_id, status, changed_by, comment, changed_at) FROM stdin;
\.


--
-- Data for Name: teacher_comments; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.teacher_comments (id, report_id, field_id, teacher_id, text, created_at) FROM stdin;
\.


--
-- Data for Name: teacher_groups; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.teacher_groups (teacher_id, group_id) FROM stdin;
\.


--
-- Data for Name: teacher_overrides; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.teacher_overrides (id, report_id, field_id, teacher_id, override_type, old_value, new_value, reason, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.users (id, role, login, password_hash, last_name, first_name, middle_name, group_id, selectable_for_students, status, created_at, updated_at) FROM stdin;
\.


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 1, false);


--
-- Name: groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.groups_id_seq', 1, false);


--
-- Name: lab_fields_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.lab_fields_id_seq', 1, false);


--
-- Name: lab_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.lab_reports_id_seq', 1, false);


--
-- Name: labs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.labs_id_seq', 1, false);


--
-- Name: ml_runs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.ml_runs_id_seq', 1, false);


--
-- Name: report_attachments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.report_attachments_id_seq', 1, false);


--
-- Name: report_field_errors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.report_field_errors_id_seq', 1, false);


--
-- Name: report_field_values_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.report_field_values_id_seq', 1, false);


--
-- Name: report_status_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.report_status_history_id_seq', 1, false);


--
-- Name: teacher_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.teacher_comments_id_seq', 1, false);


--
-- Name: teacher_overrides_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.teacher_overrides_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: groups groups_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_name_key UNIQUE (name);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: lab_fields lab_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lab_fields
    ADD CONSTRAINT lab_fields_pkey PRIMARY KEY (id);


--
-- Name: lab_reports lab_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lab_reports
    ADD CONSTRAINT lab_reports_pkey PRIMARY KEY (id);


--
-- Name: labs labs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.labs
    ADD CONSTRAINT labs_pkey PRIMARY KEY (id);


--
-- Name: ml_runs ml_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ml_runs
    ADD CONSTRAINT ml_runs_pkey PRIMARY KEY (id);


--
-- Name: report_attachments report_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_attachments
    ADD CONSTRAINT report_attachments_pkey PRIMARY KEY (id);


--
-- Name: report_field_errors report_field_errors_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_field_errors
    ADD CONSTRAINT report_field_errors_pkey PRIMARY KEY (id);


--
-- Name: report_field_values report_field_values_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_field_values
    ADD CONSTRAINT report_field_values_pkey PRIMARY KEY (id);


--
-- Name: report_status_history report_status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_status_history
    ADD CONSTRAINT report_status_history_pkey PRIMARY KEY (id);


--
-- Name: teacher_comments teacher_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_comments
    ADD CONSTRAINT teacher_comments_pkey PRIMARY KEY (id);


--
-- Name: teacher_groups teacher_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_groups
    ADD CONSTRAINT teacher_groups_pkey PRIMARY KEY (teacher_id, group_id);


--
-- Name: teacher_overrides teacher_overrides_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_overrides
    ADD CONSTRAINT teacher_overrides_pkey PRIMARY KEY (id);


--
-- Name: lab_fields uq_lab_fields_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lab_fields
    ADD CONSTRAINT uq_lab_fields_key UNIQUE (lab_id, field_key);


--
-- Name: lab_reports uq_report_student_lab; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lab_reports
    ADD CONSTRAINT uq_report_student_lab UNIQUE (student_id, lab_id);


--
-- Name: report_field_values uq_value_report_field; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_field_values
    ADD CONSTRAINT uq_value_report_field UNIQUE (report_id, field_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_actor; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_audit_actor ON public.audit_log USING btree (actor_id);


--
-- Name: idx_lab_reports_status; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_lab_reports_status ON public.lab_reports USING btree (status);


--
-- Name: idx_ml_report; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_ml_report ON public.ml_runs USING btree (report_id);


--
-- Name: idx_ra_report; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_ra_report ON public.report_attachments USING btree (report_id);


--
-- Name: idx_rfe_value; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_rfe_value ON public.report_field_errors USING btree (value_id);


--
-- Name: idx_rfv_field; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_rfv_field ON public.report_field_values USING btree (field_id);


--
-- Name: idx_rsh_report; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_rsh_report ON public.report_status_history USING btree (report_id, changed_at);


--
-- Name: idx_tc_teacher; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_tc_teacher ON public.teacher_comments USING btree (teacher_id);


--
-- Name: idx_teacher_groups_group; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_teacher_groups_group ON public.teacher_groups USING btree (group_id);


--
-- Name: idx_to_report; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_to_report ON public.teacher_overrides USING btree (report_id);


--
-- Name: idx_users_role; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_users_role ON public.users USING btree (role);


--
-- Name: labs trg_labs_updated; Type: TRIGGER; Schema: public; Owner: admin
--

CREATE TRIGGER trg_labs_updated BEFORE UPDATE ON public.labs FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: report_field_values trg_rfv_updated; Type: TRIGGER; Schema: public; Owner: admin
--

CREATE TRIGGER trg_rfv_updated BEFORE UPDATE ON public.report_field_values FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: users trg_users_updated; Type: TRIGGER; Schema: public; Owner: admin
--

CREATE TRIGGER trg_users_updated BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: audit_log audit_log_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: lab_fields lab_fields_lab_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lab_fields
    ADD CONSTRAINT lab_fields_lab_id_fkey FOREIGN KEY (lab_id) REFERENCES public.labs(id) ON DELETE CASCADE;


--
-- Name: lab_reports lab_reports_graded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lab_reports
    ADD CONSTRAINT lab_reports_graded_by_fkey FOREIGN KEY (graded_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: lab_reports lab_reports_lab_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lab_reports
    ADD CONSTRAINT lab_reports_lab_id_fkey FOREIGN KEY (lab_id) REFERENCES public.labs(id) ON DELETE RESTRICT;


--
-- Name: lab_reports lab_reports_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lab_reports
    ADD CONSTRAINT lab_reports_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: labs labs_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.labs
    ADD CONSTRAINT labs_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: ml_runs ml_runs_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.ml_runs
    ADD CONSTRAINT ml_runs_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.lab_reports(id) ON DELETE CASCADE;


--
-- Name: report_attachments report_attachments_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_attachments
    ADD CONSTRAINT report_attachments_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.lab_reports(id) ON DELETE CASCADE;


--
-- Name: report_field_errors report_field_errors_value_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_field_errors
    ADD CONSTRAINT report_field_errors_value_id_fkey FOREIGN KEY (value_id) REFERENCES public.report_field_values(id) ON DELETE CASCADE;


--
-- Name: report_field_values report_field_values_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_field_values
    ADD CONSTRAINT report_field_values_field_id_fkey FOREIGN KEY (field_id) REFERENCES public.lab_fields(id) ON DELETE RESTRICT;


--
-- Name: report_field_values report_field_values_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_field_values
    ADD CONSTRAINT report_field_values_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.lab_reports(id) ON DELETE CASCADE;


--
-- Name: report_status_history report_status_history_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_status_history
    ADD CONSTRAINT report_status_history_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: report_status_history report_status_history_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.report_status_history
    ADD CONSTRAINT report_status_history_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.lab_reports(id) ON DELETE CASCADE;


--
-- Name: teacher_comments teacher_comments_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_comments
    ADD CONSTRAINT teacher_comments_field_id_fkey FOREIGN KEY (field_id) REFERENCES public.lab_fields(id) ON DELETE SET NULL;


--
-- Name: teacher_comments teacher_comments_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_comments
    ADD CONSTRAINT teacher_comments_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.lab_reports(id) ON DELETE CASCADE;


--
-- Name: teacher_comments teacher_comments_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_comments
    ADD CONSTRAINT teacher_comments_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: teacher_groups teacher_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_groups
    ADD CONSTRAINT teacher_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE CASCADE;


--
-- Name: teacher_groups teacher_groups_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_groups
    ADD CONSTRAINT teacher_groups_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: teacher_overrides teacher_overrides_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_overrides
    ADD CONSTRAINT teacher_overrides_field_id_fkey FOREIGN KEY (field_id) REFERENCES public.lab_fields(id) ON DELETE RESTRICT;


--
-- Name: teacher_overrides teacher_overrides_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_overrides
    ADD CONSTRAINT teacher_overrides_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.lab_reports(id) ON DELETE CASCADE;


--
-- Name: teacher_overrides teacher_overrides_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.teacher_overrides
    ADD CONSTRAINT teacher_overrides_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: users users_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id) ON DELETE RESTRICT;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: admin
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict TPPLP9RFVJzdKMxDQ4G0jGUZNpuchaDhoe9CN6UduR6YwWcx1waAdjIImEgdSDy

