--
-- PostgreSQL database dump
--

\restrict l9Zb7xsyQK1DmxzECdT5wh84LUNGT7iMCvzf2h3VzObUBmGshzO9bNI1c4piSu5

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-02-24 12:09:12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
--SET transaction_timeout = 0;
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
-- TOC entry 235 (class 1259 OID 24779)
-- Name: violation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.violation (
    id integer NOT NULL,
    student_id integer NOT NULL,
    class_id integer,
    staff_id integer,
    violation_name text,
    lesson_name text,
    period integer,
    statement_of_receipt text,
    parental_consent character varying(32),
    referral text,
    date date,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.violation OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 24778)
-- Name: violation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.violation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.violation_id_seq OWNER TO postgres;

--
-- TOC entry 5060 (class 0 OID 0)
-- Dependencies: 234
-- Name: violation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.violation_id_seq OWNED BY public.violation.id;


--
-- TOC entry 4902 (class 2604 OID 24782)
-- Name: violation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violation ALTER COLUMN id SET DEFAULT nextval('public.violation_id_seq'::regclass);


--
-- TOC entry 5054 (class 0 OID 24779)
-- Dependencies: 235
-- Data for Name: violation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.violation (id, student_id, class_id, staff_id, violation_name, lesson_name, period, statement_of_receipt, parental_consent, referral, date, created_at) FROM stdin;
\.


--
-- TOC entry 5061 (class 0 OID 0)
-- Dependencies: 234
-- Name: violation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.violation_id_seq', 1, false);


--
-- TOC entry 4905 (class 2606 OID 24789)
-- Name: violation violation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violation
    ADD CONSTRAINT violation_pkey PRIMARY KEY (id);


-- Completed on 2026-02-24 12:09:12

--
-- PostgreSQL database dump complete
--

\unrestrict l9Zb7xsyQK1DmxzECdT5wh84LUNGT7iMCvzf2h3VzObUBmGshzO9bNI1c4piSu5

