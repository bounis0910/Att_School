--
-- PostgreSQL database dump
--

\restrict wBEoaehoNwK8xphoU2IgfAYiWlJTF0TkVbtrdPOJaw32Sswl6UFcyrGznTHaLvM

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

-- Started on 2026-02-23 10:33:40

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
-- TOC entry 241 (class 1259 OID 24822)
-- Name: performance_level; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.performance_level (
    id integer NOT NULL,
    name text NOT NULL,
    status character varying(32) DEFAULT 'active'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.performance_level OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 24821)
-- Name: performance_level_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.performance_level_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.performance_level_id_seq OWNER TO postgres;

--
-- TOC entry 5064 (class 0 OID 0)
-- Dependencies: 240
-- Name: performance_level_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.performance_level_id_seq OWNED BY public.performance_level.id;


--
-- TOC entry 4902 (class 2604 OID 24825)
-- Name: performance_level id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_level ALTER COLUMN id SET DEFAULT nextval('public.performance_level_id_seq'::regclass);


--
-- TOC entry 5058 (class 0 OID 24822)
-- Dependencies: 241
-- Data for Name: performance_level; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.performance_level (id, name, status, created_at, updated_at) FROM stdin;
1	ضعيف	active	2026-02-22 09:26:10.16959+03	2026-02-22 09:26:10.16959+03
2	متوسط	active	2026-02-22 09:26:16.464314+03	2026-02-22 09:26:16.464314+03
3	جيد	active	2026-02-22 09:26:21.51972+03	2026-02-22 09:26:21.51972+03
4	متميز	active	2026-02-22 09:26:28.270995+03	2026-02-22 09:26:28.270995+03
\.


--
-- TOC entry 5065 (class 0 OID 0)
-- Dependencies: 240
-- Name: performance_level_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.performance_level_id_seq', 4, true);


--
-- TOC entry 4907 (class 2606 OID 24837)
-- Name: performance_level performance_level_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_level
    ADD CONSTRAINT performance_level_name_key UNIQUE (name);


--
-- TOC entry 4909 (class 2606 OID 24835)
-- Name: performance_level performance_level_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_level
    ADD CONSTRAINT performance_level_pkey PRIMARY KEY (id);


-- Completed on 2026-02-23 10:33:40

--
-- PostgreSQL database dump complete
--

\unrestrict wBEoaehoNwK8xphoU2IgfAYiWlJTF0TkVbtrdPOJaw32Sswl6UFcyrGznTHaLvM

