--
-- PostgreSQL database dump
--

\restrict Be0FTDKr3alEcRUILnf5t69HRlfzEcMTh1v7bIHERJyRgZgsn76j6whGlh7XS74

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-02-23 10:32:09

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
-- SET transaction_timeout = 0;
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
-- TOC entry 243 (class 1259 OID 24839)
-- Name: performance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.performance (
    id integer NOT NULL,
    student_id integer NOT NULL,
    class_id integer,
    teacher_id integer,
    week_number integer NOT NULL,
    year integer NOT NULL,
    level_id integer,
    level_name text,
    comment text,
    status character varying(32) DEFAULT 'active'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.performance OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 24838)
-- Name: performance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.performance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.performance_id_seq OWNER TO postgres;

--
-- TOC entry 5064 (class 0 OID 0)
-- Dependencies: 242
-- Name: performance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.performance_id_seq OWNED BY public.performance.id;


--
-- TOC entry 4902 (class 2604 OID 24842)
-- Name: performance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance ALTER COLUMN id SET DEFAULT nextval('public.performance_id_seq'::regclass);


--
-- TOC entry 5058 (class 0 OID 24839)
-- Dependencies: 243
-- Data for Name: performance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.performance (id, student_id, class_id, teacher_id, week_number, year, level_id, level_name, comment, status, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5065 (class 0 OID 0)
-- Dependencies: 242
-- Name: performance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.performance_id_seq', 1, false);


--
-- TOC entry 4909 (class 2606 OID 24853)
-- Name: performance performance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT performance_pkey PRIMARY KEY (id);


--
-- TOC entry 4906 (class 1259 OID 24855)
-- Name: idx_performance_class_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_performance_class_week ON public.performance USING btree (class_id, week_number);


--
-- TOC entry 4907 (class 1259 OID 24854)
-- Name: idx_performance_student_week; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_performance_student_week ON public.performance USING btree (student_id, week_number);


-- Completed on 2026-02-23 10:32:09

--
-- PostgreSQL database dump complete
--

\unrestrict Be0FTDKr3alEcRUILnf5t69HRlfzEcMTh1v7bIHERJyRgZgsn76j6whGlh7XS74

