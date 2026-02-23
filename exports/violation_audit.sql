--
-- PostgreSQL database dump
--

\restrict 1dz7GPznTSMVZKhWoSQa8hops1AT1lR8KOsmQ52vbCzanFdRkF3pqT549UpBLtv

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-02-23 12:11:30

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 237 (class 1259 OID 24791)
-- Name: violation_audit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.violation_audit (
    id integer NOT NULL,
    violation_id integer,
    action character varying(32),
    user_id integer,
    username text,
    details jsonb,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.violation_audit OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 24790)
-- Name: violation_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.violation_audit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.violation_audit_id_seq OWNER TO postgres;

--
-- TOC entry 5060 (class 0 OID 0)
-- Dependencies: 236
-- Name: violation_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.violation_audit_id_seq OWNED BY public.violation_audit.id;


--
-- TOC entry 4902 (class 2604 OID 24794)
-- Name: violation_audit id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violation_audit ALTER COLUMN id SET DEFAULT nextval('public.violation_audit_id_seq'::regclass);


--
-- TOC entry 5054 (class 0 OID 24791)
-- Dependencies: 237
-- Data for Name: violation_audit; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.violation_audit (id, violation_id, action, user_id, username, details, created_at) FROM stdin;
\.


--
-- TOC entry 5061 (class 0 OID 0)
-- Dependencies: 236
-- Name: violation_audit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.violation_audit_id_seq', 1, false);


--
-- TOC entry 4905 (class 2606 OID 24800)
-- Name: violation_audit violation_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violation_audit
    ADD CONSTRAINT violation_audit_pkey PRIMARY KEY (id);


-- Completed on 2026-02-23 12:11:31

--
-- PostgreSQL database dump complete
--

\unrestrict 1dz7GPznTSMVZKhWoSQa8hops1AT1lR8KOsmQ52vbCzanFdRkF3pqT549UpBLtv

