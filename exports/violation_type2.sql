--
-- PostgreSQL database dump
--

\restrict baZKkyULe8195ZkLiJDNBbS01RaEspqpVZP6HeldX05KrQUoWoI3fD3fEjUKpEk

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-02-24 12:18:24

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
-- TOC entry 239 (class 1259 OID 24802)
-- Name: violation_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.violation_type (
    id integer NOT NULL,
    name text NOT NULL,
    status character varying(32) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.violation_type OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 24801)
-- Name: violation_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.violation_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.violation_type_id_seq OWNER TO postgres;

--
-- TOC entry 5065 (class 0 OID 0)
-- Dependencies: 238
-- Name: violation_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.violation_type_id_seq OWNED BY public.violation_type.id;


--
-- TOC entry 4902 (class 2604 OID 24805)
-- Name: violation_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violation_type ALTER COLUMN id SET DEFAULT nextval('public.violation_type_id_seq'::regclass);


--
-- TOC entry 5059 (class 0 OID 24802)
-- Dependencies: 239
-- Data for Name: violation_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.violation_type (id, name, status, created_at, updated_at) FROM stdin;
1	نوم متكرر في الحصص	active	2026-02-22 12:07:21.402263+03	2026-02-22 12:07:21.402263+03
2	عدم إحضار الأدوات	active	2026-02-22 12:07:29.095881+03	2026-02-22 12:07:29.095881+03
3	الخروج والاستئذان المتكرر من الصف	active	2026-02-22 12:07:35.18527+03	2026-02-22 12:07:35.18527+03
4	إثارة الفوضى أثناء الحصة	active	2026-02-22 12:07:41.063225+03	2026-02-22 12:07:41.063225+03
5	عدم الالتزام بالزي الرياضي	active	2026-02-22 12:07:49.502026+03	2026-02-22 12:07:49.502026+03
6	عدم الكتابة أثناءالحصة	active	2026-02-22 12:07:58.170382+03	2026-02-22 12:07:58.170382+03
7	التأخير عن دخول الحصة	active	2026-02-22 12:08:04.252369+03	2026-02-22 12:08:04.252369+03
\.


--
-- TOC entry 5066 (class 0 OID 0)
-- Dependencies: 238
-- Name: violation_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.violation_type_id_seq', 7, true);


--
-- TOC entry 4908 (class 2606 OID 24819)
-- Name: violation_type violation_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violation_type
    ADD CONSTRAINT violation_type_name_key UNIQUE (name);


--
-- TOC entry 4910 (class 2606 OID 24817)
-- Name: violation_type violation_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.violation_type
    ADD CONSTRAINT violation_type_pkey PRIMARY KEY (id);


--
-- TOC entry 4906 (class 1259 OID 24820)
-- Name: idx_violation_type_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_violation_type_status ON public.violation_type USING btree (status);


-- Completed on 2026-02-24 12:18:24

--
-- PostgreSQL database dump complete
--

\unrestrict baZKkyULe8195ZkLiJDNBbS01RaEspqpVZP6HeldX05KrQUoWoI3fD3fEjUKpEk

