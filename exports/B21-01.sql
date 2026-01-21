--
-- PostgreSQL database dump
--

\restrict elZ0B7wgDy0x4Q4ewcS5fA1A4fj1EN0bbceYmmdEQVqiLKbu9YpsQ6qI1p2qrez

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

-- Started on 2026-01-21 23:45:43 +03

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 228 (class 1259 OID 16484)
-- Name: attendance; Type: TABLE; Schema: public; Owner: adminit
--

CREATE TABLE public.attendance (
    id integer NOT NULL,
    student_id integer NOT NULL,
    class_id integer NOT NULL,
    period integer NOT NULL,
    teacher_id integer NOT NULL,
    date date NOT NULL,
    status character varying(20) DEFAULT 'absent'::character varying,
    remark character varying(255),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.attendance OWNER TO adminit;

--
-- TOC entry 227 (class 1259 OID 16483)
-- Name: attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: adminit
--

CREATE SEQUENCE public.attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_id_seq OWNER TO adminit;

--
-- TOC entry 3581 (class 0 OID 0)
-- Dependencies: 227
-- Name: attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: adminit
--

ALTER SEQUENCE public.attendance_id_seq OWNED BY public.attendance.id;


--
-- TOC entry 220 (class 1259 OID 16417)
-- Name: period; Type: TABLE; Schema: public; Owner: adminit
--

CREATE TABLE public.period (
    id integer NOT NULL,
    period_num integer NOT NULL,
    class_id integer,
    teacher_id integer,
    start_time time without time zone,
    end_time time without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    day_of_week integer
);


ALTER TABLE public.period OWNER TO adminit;

--
-- TOC entry 219 (class 1259 OID 16416)
-- Name: period_id_seq; Type: SEQUENCE; Schema: public; Owner: adminit
--

CREATE SEQUENCE public.period_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.period_id_seq OWNER TO adminit;

--
-- TOC entry 3582 (class 0 OID 0)
-- Dependencies: 219
-- Name: period_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: adminit
--

ALTER SEQUENCE public.period_id_seq OWNED BY public.period.id;


--
-- TOC entry 218 (class 1259 OID 16402)
-- Name: school_class; Type: TABLE; Schema: public; Owner: adminit
--

CREATE TABLE public.school_class (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    teacher_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.school_class OWNER TO adminit;

--
-- TOC entry 217 (class 1259 OID 16401)
-- Name: school_class_id_seq; Type: SEQUENCE; Schema: public; Owner: adminit
--

CREATE SEQUENCE public.school_class_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.school_class_id_seq OWNER TO adminit;

--
-- TOC entry 3583 (class 0 OID 0)
-- Dependencies: 217
-- Name: school_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: adminit
--

ALTER SEQUENCE public.school_class_id_seq OWNED BY public.school_class.id;


--
-- TOC entry 222 (class 1259 OID 16437)
-- Name: student; Type: TABLE; Schema: public; Owner: adminit
--

CREATE TABLE public.student (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    roll_number character varying(20) NOT NULL,
    class_id integer NOT NULL,
    email character varying(100),
    phone character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.student OWNER TO adminit;

--
-- TOC entry 221 (class 1259 OID 16436)
-- Name: student_id_seq; Type: SEQUENCE; Schema: public; Owner: adminit
--

CREATE SEQUENCE public.student_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_id_seq OWNER TO adminit;

--
-- TOC entry 3584 (class 0 OID 0)
-- Dependencies: 221
-- Name: student_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: adminit
--

ALTER SEQUENCE public.student_id_seq OWNED BY public.student.id;


--
-- TOC entry 224 (class 1259 OID 16452)
-- Name: subject; Type: TABLE; Schema: public; Owner: adminit
--

CREATE TABLE public.subject (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.subject OWNER TO adminit;

--
-- TOC entry 223 (class 1259 OID 16451)
-- Name: subject_id_seq; Type: SEQUENCE; Schema: public; Owner: adminit
--

CREATE SEQUENCE public.subject_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subject_id_seq OWNER TO adminit;

--
-- TOC entry 3585 (class 0 OID 0)
-- Dependencies: 223
-- Name: subject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: adminit
--

ALTER SEQUENCE public.subject_id_seq OWNED BY public.subject.id;


--
-- TOC entry 226 (class 1259 OID 16464)
-- Name: teacher_subject; Type: TABLE; Schema: public; Owner: adminit
--

CREATE TABLE public.teacher_subject (
    id integer NOT NULL,
    teacher_id integer NOT NULL,
    subject_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    class_id integer
);


ALTER TABLE public.teacher_subject OWNER TO adminit;

--
-- TOC entry 225 (class 1259 OID 16463)
-- Name: teacher_subject_id_seq; Type: SEQUENCE; Schema: public; Owner: adminit
--

CREATE SEQUENCE public.teacher_subject_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teacher_subject_id_seq OWNER TO adminit;

--
-- TOC entry 3586 (class 0 OID 0)
-- Dependencies: 225
-- Name: teacher_subject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: adminit
--

ALTER SEQUENCE public.teacher_subject_id_seq OWNED BY public.teacher_subject.id;


--
-- TOC entry 216 (class 1259 OID 16392)
-- Name: user; Type: TABLE; Schema: public; Owner: adminit
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    national_id character(11),
    classes character(100),
    email character(100),
    emp_id character(10)
);


ALTER TABLE public."user" OWNER TO adminit;

--
-- TOC entry 215 (class 1259 OID 16391)
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: adminit
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO adminit;

--
-- TOC entry 3587 (class 0 OID 0)
-- Dependencies: 215
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: adminit
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- TOC entry 3363 (class 2604 OID 16487)
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- TOC entry 3355 (class 2604 OID 16420)
-- Name: period id; Type: DEFAULT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.period ALTER COLUMN id SET DEFAULT nextval('public.period_id_seq'::regclass);


--
-- TOC entry 3353 (class 2604 OID 16405)
-- Name: school_class id; Type: DEFAULT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.school_class ALTER COLUMN id SET DEFAULT nextval('public.school_class_id_seq'::regclass);


--
-- TOC entry 3357 (class 2604 OID 16440)
-- Name: student id; Type: DEFAULT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.student ALTER COLUMN id SET DEFAULT nextval('public.student_id_seq'::regclass);


--
-- TOC entry 3359 (class 2604 OID 16455)
-- Name: subject id; Type: DEFAULT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.subject ALTER COLUMN id SET DEFAULT nextval('public.subject_id_seq'::regclass);


--
-- TOC entry 3361 (class 2604 OID 16467)
-- Name: teacher_subject id; Type: DEFAULT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.teacher_subject ALTER COLUMN id SET DEFAULT nextval('public.teacher_subject_id_seq'::regclass);


--
-- TOC entry 3351 (class 2604 OID 16395)
-- Name: user id; Type: DEFAULT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- TOC entry 3575 (class 0 OID 16484)
-- Dependencies: 228
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: adminit
--

COPY public.attendance (id, student_id, class_id, period, teacher_id, date, status, remark, notes, created_at, updated_at) FROM stdin;
550	98	4	3	14	2025-12-13	absent	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
551	99	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
552	100	4	3	14	2025-12-13	absent	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
553	101	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
554	102	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
555	103	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
556	104	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
557	105	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
558	106	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
559	107	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
560	108	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
561	109	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
562	110	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
563	111	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
564	112	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
565	113	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
566	114	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
567	115	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
568	116	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
569	117	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
570	118	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
571	119	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
572	120	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
573	121	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
574	122	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
575	123	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
576	124	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
577	125	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
578	126	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
579	127	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
580	128	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
581	129	4	3	14	2025-12-13	present	\N	\N	2025-12-13 14:39:57.340605	2025-12-13 14:39:57.340605
485	1	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
486	2	1	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
487	3	1	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
488	4	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
489	5	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
490	6	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
491	7	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
492	8	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
493	9	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
494	10	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
495	11	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
496	12	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
497	13	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
498	14	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
499	15	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
500	16	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
501	17	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
502	18	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
503	19	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
504	20	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
505	21	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
506	22	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
507	23	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
508	24	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
509	25	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
510	26	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
511	27	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
512	28	1	1	11	2025-11-30	present	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
513	29	1	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
514	30	1	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
515	31	1	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
516	32	1	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
517	33	1	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:33:34.256094	2025-11-30 14:33:34.256094
518	34	2	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
519	35	2	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
520	36	2	1	11	2025-11-30	absent	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
521	37	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
522	38	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
523	39	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
524	40	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
525	41	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
526	42	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
527	43	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
528	44	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
529	45	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
530	46	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
531	47	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
532	48	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
533	49	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
534	50	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
535	51	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
536	52	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
537	53	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
538	54	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
539	55	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
540	56	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
541	57	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
542	58	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
543	59	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
544	60	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
545	61	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
546	62	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
547	63	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
548	64	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
549	65	2	1	11	2025-11-30	present	\N	\N	2025-11-30 14:40:37.956832	2025-11-30 14:40:37.956832
102	5	1	11	9	2025-11-25	present	\N	\N	\N	\N
1	1	1	1	10	2025-11-25	absent	excused	\N	\N	\N
2	2	1	1	10	2025-11-25	absent	excused	\N	\N	\N
3	3	1	1	10	2025-11-25	absent	excused	\N	\N	\N
4	4	1	1	10	2025-11-25	present	\N	\N	\N	\N
5	5	1	1	10	2025-11-25	present	\N	\N	\N	\N
6	6	1	1	10	2025-11-25	present	\N	\N	\N	\N
7	7	1	1	10	2025-11-25	present	\N	\N	\N	\N
8	8	1	1	10	2025-11-25	present	\N	\N	\N	\N
9	9	1	1	10	2025-11-25	present	\N	\N	\N	\N
10	10	1	1	10	2025-11-25	present	\N	\N	\N	\N
11	11	1	1	10	2025-11-25	present	\N	\N	\N	\N
12	12	1	1	10	2025-11-25	present	\N	\N	\N	\N
13	13	1	1	10	2025-11-25	present	\N	\N	\N	\N
14	14	1	1	10	2025-11-25	present	\N	\N	\N	\N
15	15	1	1	10	2025-11-25	present	\N	\N	\N	\N
16	16	1	1	10	2025-11-25	present	\N	\N	\N	\N
17	17	1	1	10	2025-11-25	present	\N	\N	\N	\N
18	18	1	1	10	2025-11-25	present	\N	\N	\N	\N
19	19	1	1	10	2025-11-25	present	\N	\N	\N	\N
20	20	1	1	10	2025-11-25	present	\N	\N	\N	\N
21	21	1	1	10	2025-11-25	present	\N	\N	\N	\N
22	22	1	1	10	2025-11-25	present	\N	\N	\N	\N
23	23	1	1	10	2025-11-25	present	\N	\N	\N	\N
24	24	1	1	10	2025-11-25	present	\N	\N	\N	\N
25	25	1	1	10	2025-11-25	present	\N	\N	\N	\N
26	26	1	1	10	2025-11-25	present	\N	\N	\N	\N
27	27	1	1	10	2025-11-25	present	\N	\N	\N	\N
28	28	1	1	10	2025-11-25	present	\N	\N	\N	\N
29	29	1	1	10	2025-11-25	present	\N	\N	\N	\N
30	30	1	1	10	2025-11-25	present	\N	\N	\N	\N
31	31	1	1	10	2025-11-25	present	\N	\N	\N	\N
32	32	1	1	10	2025-11-25	present	\N	\N	\N	\N
33	33	1	1	10	2025-11-25	present	\N	\N	\N	\N
34	66	3	10	9	2025-11-25	absent	excused	\N	\N	\N
35	67	3	10	9	2025-11-25	absent	excused	\N	\N	\N
36	68	3	10	9	2025-11-25	present	\N	\N	\N	\N
37	69	3	10	9	2025-11-25	absent	excused	\N	\N	\N
38	70	3	10	9	2025-11-25	absent	excused	\N	\N	\N
39	71	3	10	9	2025-11-25	present	\N	\N	\N	\N
40	72	3	10	9	2025-11-25	present	\N	\N	\N	\N
41	73	3	10	9	2025-11-25	present	\N	\N	\N	\N
42	74	3	10	9	2025-11-25	present	\N	\N	\N	\N
43	75	3	10	9	2025-11-25	present	\N	\N	\N	\N
44	76	3	10	9	2025-11-25	present	\N	\N	\N	\N
45	77	3	10	9	2025-11-25	present	\N	\N	\N	\N
46	78	3	10	9	2025-11-25	present	\N	\N	\N	\N
47	79	3	10	9	2025-11-25	present	\N	\N	\N	\N
48	80	3	10	9	2025-11-25	present	\N	\N	\N	\N
49	81	3	10	9	2025-11-25	present	\N	\N	\N	\N
50	82	3	10	9	2025-11-25	present	\N	\N	\N	\N
51	83	3	10	9	2025-11-25	present	\N	\N	\N	\N
52	84	3	10	9	2025-11-25	present	\N	\N	\N	\N
53	85	3	10	9	2025-11-25	present	\N	\N	\N	\N
54	86	3	10	9	2025-11-25	present	\N	\N	\N	\N
55	87	3	10	9	2025-11-25	present	\N	\N	\N	\N
56	88	3	10	9	2025-11-25	present	\N	\N	\N	\N
57	89	3	10	9	2025-11-25	present	\N	\N	\N	\N
58	90	3	10	9	2025-11-25	present	\N	\N	\N	\N
59	91	3	10	9	2025-11-25	present	\N	\N	\N	\N
60	92	3	10	9	2025-11-25	present	\N	\N	\N	\N
61	93	3	10	9	2025-11-25	present	\N	\N	\N	\N
62	94	3	10	9	2025-11-25	present	\N	\N	\N	\N
63	95	3	10	9	2025-11-25	present	\N	\N	\N	\N
64	96	3	10	9	2025-11-25	present	\N	\N	\N	\N
65	97	3	10	9	2025-11-25	present	\N	\N	\N	\N
66	98	4	10	84	2025-11-25	absent	excused	\N	\N	\N
67	99	4	10	84	2025-11-25	present	\N	\N	\N	\N
68	100	4	10	84	2025-11-25	present	\N	\N	\N	\N
69	101	4	10	84	2025-11-25	present	\N	\N	\N	\N
70	102	4	10	84	2025-11-25	present	\N	\N	\N	\N
71	103	4	10	84	2025-11-25	present	\N	\N	\N	\N
72	104	4	10	84	2025-11-25	present	\N	\N	\N	\N
73	105	4	10	84	2025-11-25	present	\N	\N	\N	\N
74	106	4	10	84	2025-11-25	present	\N	\N	\N	\N
75	107	4	10	84	2025-11-25	present	\N	\N	\N	\N
76	108	4	10	84	2025-11-25	present	\N	\N	\N	\N
77	109	4	10	84	2025-11-25	present	\N	\N	\N	\N
78	110	4	10	84	2025-11-25	present	\N	\N	\N	\N
79	111	4	10	84	2025-11-25	present	\N	\N	\N	\N
80	112	4	10	84	2025-11-25	present	\N	\N	\N	\N
81	113	4	10	84	2025-11-25	present	\N	\N	\N	\N
82	114	4	10	84	2025-11-25	present	\N	\N	\N	\N
83	115	4	10	84	2025-11-25	present	\N	\N	\N	\N
84	116	4	10	84	2025-11-25	present	\N	\N	\N	\N
85	117	4	10	84	2025-11-25	present	\N	\N	\N	\N
86	118	4	10	84	2025-11-25	present	\N	\N	\N	\N
87	119	4	10	84	2025-11-25	present	\N	\N	\N	\N
88	120	4	10	84	2025-11-25	present	\N	\N	\N	\N
89	121	4	10	84	2025-11-25	present	\N	\N	\N	\N
90	122	4	10	84	2025-11-25	present	\N	\N	\N	\N
91	123	4	10	84	2025-11-25	present	\N	\N	\N	\N
92	124	4	10	84	2025-11-25	present	\N	\N	\N	\N
93	125	4	10	84	2025-11-25	present	\N	\N	\N	\N
94	126	4	10	84	2025-11-25	present	\N	\N	\N	\N
95	127	4	10	84	2025-11-25	present	\N	\N	\N	\N
96	128	4	10	84	2025-11-25	present	\N	\N	\N	\N
97	129	4	10	84	2025-11-25	present	\N	\N	\N	\N
98	1	1	11	9	2025-11-25	absent	\N	\N	\N	\N
99	2	1	11	9	2025-11-25	present	\N	\N	\N	\N
100	3	1	11	9	2025-11-25	present	\N	\N	\N	\N
101	4	1	11	9	2025-11-25	present	\N	\N	\N	\N
103	6	1	11	9	2025-11-25	present	\N	\N	\N	\N
104	7	1	11	9	2025-11-25	present	\N	\N	\N	\N
105	8	1	11	9	2025-11-25	present	\N	\N	\N	\N
106	9	1	11	9	2025-11-25	present	\N	\N	\N	\N
107	10	1	11	9	2025-11-25	present	\N	\N	\N	\N
108	11	1	11	9	2025-11-25	present	\N	\N	\N	\N
109	12	1	11	9	2025-11-25	present	\N	\N	\N	\N
110	13	1	11	9	2025-11-25	present	\N	\N	\N	\N
111	14	1	11	9	2025-11-25	present	\N	\N	\N	\N
112	15	1	11	9	2025-11-25	present	\N	\N	\N	\N
113	16	1	11	9	2025-11-25	present	\N	\N	\N	\N
114	17	1	11	9	2025-11-25	present	\N	\N	\N	\N
115	18	1	11	9	2025-11-25	present	\N	\N	\N	\N
116	19	1	11	9	2025-11-25	present	\N	\N	\N	\N
117	20	1	11	9	2025-11-25	present	\N	\N	\N	\N
118	21	1	11	9	2025-11-25	present	\N	\N	\N	\N
119	22	1	11	9	2025-11-25	present	\N	\N	\N	\N
120	23	1	11	9	2025-11-25	present	\N	\N	\N	\N
121	24	1	11	9	2025-11-25	present	\N	\N	\N	\N
122	25	1	11	9	2025-11-25	present	\N	\N	\N	\N
123	26	1	11	9	2025-11-25	present	\N	\N	\N	\N
124	27	1	11	9	2025-11-25	present	\N	\N	\N	\N
125	28	1	11	9	2025-11-25	present	\N	\N	\N	\N
126	29	1	11	9	2025-11-25	present	\N	\N	\N	\N
127	30	1	11	9	2025-11-25	present	\N	\N	\N	\N
128	31	1	11	9	2025-11-25	present	\N	\N	\N	\N
129	32	1	11	9	2025-11-25	present	\N	\N	\N	\N
130	33	1	11	9	2025-11-25	present	\N	\N	\N	\N
131	130	5	11	10	2025-11-25	absent	\N	\N	\N	\N
132	131	5	11	10	2025-11-25	present	\N	\N	\N	\N
133	132	5	11	10	2025-11-25	present	\N	\N	\N	\N
134	133	5	11	10	2025-11-25	present	\N	\N	\N	\N
135	134	5	11	10	2025-11-25	present	\N	\N	\N	\N
136	135	5	11	10	2025-11-25	present	\N	\N	\N	\N
137	136	5	11	10	2025-11-25	present	\N	\N	\N	\N
138	137	5	11	10	2025-11-25	present	\N	\N	\N	\N
139	138	5	11	10	2025-11-25	present	\N	\N	\N	\N
140	139	5	11	10	2025-11-25	present	\N	\N	\N	\N
141	140	5	11	10	2025-11-25	present	\N	\N	\N	\N
142	141	5	11	10	2025-11-25	present	\N	\N	\N	\N
143	142	5	11	10	2025-11-25	present	\N	\N	\N	\N
144	143	5	11	10	2025-11-25	present	\N	\N	\N	\N
145	144	5	11	10	2025-11-25	present	\N	\N	\N	\N
146	145	5	11	10	2025-11-25	present	\N	\N	\N	\N
147	146	5	11	10	2025-11-25	present	\N	\N	\N	\N
148	147	5	11	10	2025-11-25	present	\N	\N	\N	\N
149	148	5	11	10	2025-11-25	present	\N	\N	\N	\N
150	149	5	11	10	2025-11-25	present	\N	\N	\N	\N
151	150	5	11	10	2025-11-25	present	\N	\N	\N	\N
152	151	5	11	10	2025-11-25	present	\N	\N	\N	\N
153	152	5	11	10	2025-11-25	present	\N	\N	\N	\N
154	153	5	11	10	2025-11-25	present	\N	\N	\N	\N
155	154	5	11	10	2025-11-25	present	\N	\N	\N	\N
156	155	5	11	10	2025-11-25	present	\N	\N	\N	\N
157	156	5	11	10	2025-11-25	present	\N	\N	\N	\N
158	157	5	11	10	2025-11-25	present	\N	\N	\N	\N
159	158	5	11	10	2025-11-25	present	\N	\N	\N	\N
160	159	5	11	10	2025-11-25	present	\N	\N	\N	\N
161	160	5	11	10	2025-11-25	present	\N	\N	\N	\N
162	161	6	11	84	2025-11-25	absent	\N	\N	\N	\N
163	162	6	11	84	2025-11-25	present	\N	\N	\N	\N
164	163	6	11	84	2025-11-25	present	\N	\N	\N	\N
165	164	6	11	84	2025-11-25	present	\N	\N	\N	\N
166	165	6	11	84	2025-11-25	present	\N	\N	\N	\N
167	166	6	11	84	2025-11-25	present	\N	\N	\N	\N
168	167	6	11	84	2025-11-25	present	\N	\N	\N	\N
169	168	6	11	84	2025-11-25	present	\N	\N	\N	\N
170	169	6	11	84	2025-11-25	present	\N	\N	\N	\N
171	170	6	11	84	2025-11-25	present	\N	\N	\N	\N
172	171	6	11	84	2025-11-25	present	\N	\N	\N	\N
173	172	6	11	84	2025-11-25	present	\N	\N	\N	\N
174	173	6	11	84	2025-11-25	present	\N	\N	\N	\N
175	174	6	11	84	2025-11-25	present	\N	\N	\N	\N
176	175	6	11	84	2025-11-25	present	\N	\N	\N	\N
177	176	6	11	84	2025-11-25	present	\N	\N	\N	\N
178	177	6	11	84	2025-11-25	present	\N	\N	\N	\N
179	178	6	11	84	2025-11-25	present	\N	\N	\N	\N
180	179	6	11	84	2025-11-25	present	\N	\N	\N	\N
181	180	6	11	84	2025-11-25	present	\N	\N	\N	\N
182	181	6	11	84	2025-11-25	present	\N	\N	\N	\N
183	182	6	11	84	2025-11-25	present	\N	\N	\N	\N
184	183	6	11	84	2025-11-25	present	\N	\N	\N	\N
185	184	6	11	84	2025-11-25	present	\N	\N	\N	\N
186	185	6	11	84	2025-11-25	present	\N	\N	\N	\N
187	186	6	11	84	2025-11-25	present	\N	\N	\N	\N
188	187	6	11	84	2025-11-25	present	\N	\N	\N	\N
189	188	6	11	84	2025-11-25	present	\N	\N	\N	\N
190	189	6	11	84	2025-11-25	present	\N	\N	\N	\N
191	190	6	11	84	2025-11-25	present	\N	\N	\N	\N
192	191	6	11	84	2025-11-25	present	\N	\N	\N	\N
193	192	6	11	84	2025-11-25	present	\N	\N	\N	\N
194	161	6	12	84	2025-11-25	absent	\N	\N	\N	\N
195	162	6	12	84	2025-11-25	present	\N	\N	\N	\N
196	163	6	12	84	2025-11-25	present	\N	\N	\N	\N
197	164	6	12	84	2025-11-25	present	\N	\N	\N	\N
198	165	6	12	84	2025-11-25	present	\N	\N	\N	\N
199	166	6	12	84	2025-11-25	present	\N	\N	\N	\N
200	167	6	12	84	2025-11-25	present	\N	\N	\N	\N
201	168	6	12	84	2025-11-25	present	\N	\N	\N	\N
202	169	6	12	84	2025-11-25	present	\N	\N	\N	\N
203	170	6	12	84	2025-11-25	present	\N	\N	\N	\N
204	171	6	12	84	2025-11-25	present	\N	\N	\N	\N
205	172	6	12	84	2025-11-25	present	\N	\N	\N	\N
206	173	6	12	84	2025-11-25	present	\N	\N	\N	\N
207	174	6	12	84	2025-11-25	present	\N	\N	\N	\N
208	175	6	12	84	2025-11-25	present	\N	\N	\N	\N
209	176	6	12	84	2025-11-25	present	\N	\N	\N	\N
210	177	6	12	84	2025-11-25	present	\N	\N	\N	\N
211	178	6	12	84	2025-11-25	present	\N	\N	\N	\N
212	179	6	12	84	2025-11-25	present	\N	\N	\N	\N
213	180	6	12	84	2025-11-25	present	\N	\N	\N	\N
214	181	6	12	84	2025-11-25	present	\N	\N	\N	\N
215	182	6	12	84	2025-11-25	present	\N	\N	\N	\N
216	183	6	12	84	2025-11-25	present	\N	\N	\N	\N
217	184	6	12	84	2025-11-25	present	\N	\N	\N	\N
218	185	6	12	84	2025-11-25	present	\N	\N	\N	\N
219	186	6	12	84	2025-11-25	present	\N	\N	\N	\N
220	187	6	12	84	2025-11-25	present	\N	\N	\N	\N
221	188	6	12	84	2025-11-25	present	\N	\N	\N	\N
222	189	6	12	84	2025-11-25	present	\N	\N	\N	\N
223	190	6	12	84	2025-11-25	present	\N	\N	\N	\N
224	191	6	12	84	2025-11-25	present	\N	\N	\N	\N
225	192	6	12	84	2025-11-25	present	\N	\N	\N	\N
226	130	5	12	84	2025-11-25	absent	\N	\N	\N	\N
227	131	5	12	84	2025-11-25	absent	\N	\N	\N	\N
228	132	5	12	84	2025-11-25	present	\N	\N	\N	\N
229	133	5	12	84	2025-11-25	present	\N	\N	\N	\N
230	134	5	12	84	2025-11-25	present	\N	\N	\N	\N
231	135	5	12	84	2025-11-25	present	\N	\N	\N	\N
232	136	5	12	84	2025-11-25	present	\N	\N	\N	\N
233	137	5	12	84	2025-11-25	present	\N	\N	\N	\N
234	138	5	12	84	2025-11-25	present	\N	\N	\N	\N
235	139	5	12	84	2025-11-25	present	\N	\N	\N	\N
236	140	5	12	84	2025-11-25	present	\N	\N	\N	\N
237	141	5	12	84	2025-11-25	present	\N	\N	\N	\N
238	142	5	12	84	2025-11-25	present	\N	\N	\N	\N
239	143	5	12	84	2025-11-25	present	\N	\N	\N	\N
240	144	5	12	84	2025-11-25	present	\N	\N	\N	\N
241	145	5	12	84	2025-11-25	present	\N	\N	\N	\N
242	146	5	12	84	2025-11-25	present	\N	\N	\N	\N
243	147	5	12	84	2025-11-25	present	\N	\N	\N	\N
244	148	5	12	84	2025-11-25	present	\N	\N	\N	\N
245	149	5	12	84	2025-11-25	present	\N	\N	\N	\N
246	150	5	12	84	2025-11-25	present	\N	\N	\N	\N
247	151	5	12	84	2025-11-25	present	\N	\N	\N	\N
248	152	5	12	84	2025-11-25	present	\N	\N	\N	\N
249	153	5	12	84	2025-11-25	present	\N	\N	\N	\N
250	154	5	12	84	2025-11-25	present	\N	\N	\N	\N
251	155	5	12	84	2025-11-25	present	\N	\N	\N	\N
252	156	5	12	84	2025-11-25	present	\N	\N	\N	\N
253	157	5	12	84	2025-11-25	present	\N	\N	\N	\N
254	158	5	12	84	2025-11-25	present	\N	\N	\N	\N
255	159	5	12	84	2025-11-25	present	\N	\N	\N	\N
256	160	5	12	84	2025-11-25	present	\N	\N	\N	\N
257	98	4	12	10	2025-11-25	absent	excused	\N	\N	\N
258	99	4	12	10	2025-11-25	absent	excused	\N	\N	\N
259	100	4	12	10	2025-11-25	absent	\N	\N	\N	\N
260	101	4	12	10	2025-11-25	absent	\N	\N	\N	\N
261	102	4	12	10	2025-11-25	present	\N	\N	\N	\N
262	103	4	12	10	2025-11-25	present	\N	\N	\N	\N
263	104	4	12	10	2025-11-25	present	\N	\N	\N	\N
264	105	4	12	10	2025-11-25	present	\N	\N	\N	\N
265	106	4	12	10	2025-11-25	present	\N	\N	\N	\N
266	107	4	12	10	2025-11-25	present	\N	\N	\N	\N
267	108	4	12	10	2025-11-25	present	\N	\N	\N	\N
268	109	4	12	10	2025-11-25	present	\N	\N	\N	\N
269	110	4	12	10	2025-11-25	present	\N	\N	\N	\N
270	111	4	12	10	2025-11-25	present	\N	\N	\N	\N
271	112	4	12	10	2025-11-25	present	\N	\N	\N	\N
272	113	4	12	10	2025-11-25	present	\N	\N	\N	\N
273	114	4	12	10	2025-11-25	present	\N	\N	\N	\N
274	115	4	12	10	2025-11-25	present	\N	\N	\N	\N
275	116	4	12	10	2025-11-25	present	\N	\N	\N	\N
276	117	4	12	10	2025-11-25	present	\N	\N	\N	\N
277	118	4	12	10	2025-11-25	present	\N	\N	\N	\N
278	119	4	12	10	2025-11-25	present	\N	\N	\N	\N
279	120	4	12	10	2025-11-25	present	\N	\N	\N	\N
280	121	4	12	10	2025-11-25	present	\N	\N	\N	\N
281	122	4	12	10	2025-11-25	present	\N	\N	\N	\N
282	123	4	12	10	2025-11-25	present	\N	\N	\N	\N
283	124	4	12	10	2025-11-25	present	\N	\N	\N	\N
284	125	4	12	10	2025-11-25	present	\N	\N	\N	\N
285	126	4	12	10	2025-11-25	present	\N	\N	\N	\N
286	127	4	12	10	2025-11-25	present	\N	\N	\N	\N
287	128	4	12	10	2025-11-25	present	\N	\N	\N	\N
288	129	4	12	10	2025-11-25	present	\N	\N	\N	\N
289	1	1	12	9	2025-11-25	absent	\N	\N	\N	\N
290	2	1	12	9	2025-11-25	present	\N	\N	\N	\N
291	3	1	12	9	2025-11-25	present	\N	\N	\N	\N
292	4	1	12	9	2025-11-25	present	\N	\N	\N	\N
293	5	1	12	9	2025-11-25	present	\N	\N	\N	\N
294	6	1	12	9	2025-11-25	present	\N	\N	\N	\N
295	7	1	12	9	2025-11-25	present	\N	\N	\N	\N
296	8	1	12	9	2025-11-25	present	\N	\N	\N	\N
297	9	1	12	9	2025-11-25	present	\N	\N	\N	\N
298	10	1	12	9	2025-11-25	present	\N	\N	\N	\N
299	11	1	12	9	2025-11-25	present	\N	\N	\N	\N
300	12	1	12	9	2025-11-25	present	\N	\N	\N	\N
301	13	1	12	9	2025-11-25	present	\N	\N	\N	\N
302	14	1	12	9	2025-11-25	present	\N	\N	\N	\N
303	15	1	12	9	2025-11-25	present	\N	\N	\N	\N
304	16	1	12	9	2025-11-25	present	\N	\N	\N	\N
305	17	1	12	9	2025-11-25	present	\N	\N	\N	\N
306	18	1	12	9	2025-11-25	present	\N	\N	\N	\N
307	19	1	12	9	2025-11-25	present	\N	\N	\N	\N
308	20	1	12	9	2025-11-25	present	\N	\N	\N	\N
309	21	1	12	9	2025-11-25	present	\N	\N	\N	\N
310	22	1	12	9	2025-11-25	present	\N	\N	\N	\N
311	23	1	12	9	2025-11-25	present	\N	\N	\N	\N
312	24	1	12	9	2025-11-25	present	\N	\N	\N	\N
313	25	1	12	9	2025-11-25	present	\N	\N	\N	\N
314	26	1	12	9	2025-11-25	present	\N	\N	\N	\N
315	27	1	12	9	2025-11-25	present	\N	\N	\N	\N
316	28	1	12	9	2025-11-25	present	\N	\N	\N	\N
317	29	1	12	9	2025-11-25	present	\N	\N	\N	\N
318	30	1	12	9	2025-11-25	present	\N	\N	\N	\N
319	31	1	12	9	2025-11-25	present	\N	\N	\N	\N
320	32	1	12	9	2025-11-25	present	\N	\N	\N	\N
321	33	1	12	9	2025-11-25	absent	\N	\N	\N	\N
322	161	6	13	9	2025-11-25	present	\N	\N	\N	\N
323	162	6	13	9	2025-11-25	present	\N	\N	\N	\N
324	163	6	13	9	2025-11-25	present	\N	\N	\N	\N
325	164	6	13	9	2025-11-25	present	\N	\N	\N	\N
326	165	6	13	9	2025-11-25	present	\N	\N	\N	\N
327	166	6	13	9	2025-11-25	present	\N	\N	\N	\N
328	167	6	13	9	2025-11-25	present	\N	\N	\N	\N
329	168	6	13	9	2025-11-25	present	\N	\N	\N	\N
330	169	6	13	9	2025-11-25	present	\N	\N	\N	\N
331	170	6	13	9	2025-11-25	present	\N	\N	\N	\N
332	171	6	13	9	2025-11-25	present	\N	\N	\N	\N
333	172	6	13	9	2025-11-25	present	\N	\N	\N	\N
334	173	6	13	9	2025-11-25	present	\N	\N	\N	\N
335	174	6	13	9	2025-11-25	present	\N	\N	\N	\N
336	175	6	13	9	2025-11-25	present	\N	\N	\N	\N
337	176	6	13	9	2025-11-25	present	\N	\N	\N	\N
338	177	6	13	9	2025-11-25	present	\N	\N	\N	\N
339	178	6	13	9	2025-11-25	present	\N	\N	\N	\N
340	179	6	13	9	2025-11-25	present	\N	\N	\N	\N
341	180	6	13	9	2025-11-25	present	\N	\N	\N	\N
342	181	6	13	9	2025-11-25	absent	\N	\N	\N	\N
343	182	6	13	9	2025-11-25	absent	\N	\N	\N	\N
344	183	6	13	9	2025-11-25	absent	\N	\N	\N	\N
345	184	6	13	9	2025-11-25	present	\N	\N	\N	\N
346	185	6	13	9	2025-11-25	present	\N	\N	\N	\N
347	186	6	13	9	2025-11-25	present	\N	\N	\N	\N
348	187	6	13	9	2025-11-25	absent	\N	\N	\N	\N
349	188	6	13	9	2025-11-25	absent	\N	\N	\N	\N
350	189	6	13	9	2025-11-25	absent	\N	\N	\N	\N
351	190	6	13	9	2025-11-25	present	\N	\N	\N	\N
352	191	6	13	9	2025-11-25	absent	\N	\N	\N	\N
353	192	6	13	9	2025-11-25	present	\N	\N	\N	\N
354	98	4	13	10	2025-11-25	absent	excused	\N	\N	\N
355	99	4	13	10	2025-11-25	absent	\N	\N	\N	\N
356	100	4	13	10	2025-11-25	absent	\N	\N	\N	\N
357	101	4	13	10	2025-11-25	present	\N	\N	\N	\N
358	102	4	13	10	2025-11-25	present	\N	\N	\N	\N
359	103	4	13	10	2025-11-25	present	\N	\N	\N	\N
360	104	4	13	10	2025-11-25	present	\N	\N	\N	\N
361	105	4	13	10	2025-11-25	present	\N	\N	\N	\N
362	106	4	13	10	2025-11-25	present	\N	\N	\N	\N
363	107	4	13	10	2025-11-25	present	\N	\N	\N	\N
364	108	4	13	10	2025-11-25	present	\N	\N	\N	\N
365	109	4	13	10	2025-11-25	present	\N	\N	\N	\N
366	110	4	13	10	2025-11-25	present	\N	\N	\N	\N
367	111	4	13	10	2025-11-25	present	\N	\N	\N	\N
368	112	4	13	10	2025-11-25	present	\N	\N	\N	\N
369	113	4	13	10	2025-11-25	present	\N	\N	\N	\N
370	114	4	13	10	2025-11-25	present	\N	\N	\N	\N
371	115	4	13	10	2025-11-25	present	\N	\N	\N	\N
372	116	4	13	10	2025-11-25	present	\N	\N	\N	\N
373	117	4	13	10	2025-11-25	present	\N	\N	\N	\N
374	118	4	13	10	2025-11-25	present	\N	\N	\N	\N
375	119	4	13	10	2025-11-25	present	\N	\N	\N	\N
376	120	4	13	10	2025-11-25	present	\N	\N	\N	\N
377	121	4	13	10	2025-11-25	present	\N	\N	\N	\N
378	122	4	13	10	2025-11-25	present	\N	\N	\N	\N
379	123	4	13	10	2025-11-25	present	\N	\N	\N	\N
380	124	4	13	10	2025-11-25	present	\N	\N	\N	\N
381	125	4	13	10	2025-11-25	present	\N	\N	\N	\N
382	126	4	13	10	2025-11-25	present	\N	\N	\N	\N
383	127	4	13	10	2025-11-25	present	\N	\N	\N	\N
384	128	4	13	10	2025-11-25	present	\N	\N	\N	\N
385	129	4	13	10	2025-11-25	present	\N	\N	\N	\N
386	66	3	13	84	2025-11-25	present	\N	\N	\N	\N
387	67	3	13	84	2025-11-25	present	\N	\N	\N	\N
388	68	3	13	84	2025-11-25	absent	excused	\N	\N	\N
389	69	3	13	84	2025-11-25	absent	excused	\N	\N	\N
390	70	3	13	84	2025-11-25	present	\N	\N	\N	\N
391	71	3	13	84	2025-11-25	present	\N	\N	\N	\N
392	72	3	13	84	2025-11-25	present	\N	\N	\N	\N
393	73	3	13	84	2025-11-25	present	\N	\N	\N	\N
394	74	3	13	84	2025-11-25	present	\N	\N	\N	\N
395	75	3	13	84	2025-11-25	present	\N	\N	\N	\N
396	76	3	13	84	2025-11-25	present	\N	\N	\N	\N
397	77	3	13	84	2025-11-25	present	\N	\N	\N	\N
398	78	3	13	84	2025-11-25	present	\N	\N	\N	\N
399	79	3	13	84	2025-11-25	present	\N	\N	\N	\N
400	80	3	13	84	2025-11-25	present	\N	\N	\N	\N
401	81	3	13	84	2025-11-25	present	\N	\N	\N	\N
402	82	3	13	84	2025-11-25	present	\N	\N	\N	\N
403	83	3	13	84	2025-11-25	present	\N	\N	\N	\N
404	84	3	13	84	2025-11-25	present	\N	\N	\N	\N
405	85	3	13	84	2025-11-25	present	\N	\N	\N	\N
406	86	3	13	84	2025-11-25	present	\N	\N	\N	\N
407	87	3	13	84	2025-11-25	present	\N	\N	\N	\N
408	88	3	13	84	2025-11-25	present	\N	\N	\N	\N
409	89	3	13	84	2025-11-25	present	\N	\N	\N	\N
410	90	3	13	84	2025-11-25	present	\N	\N	\N	\N
411	91	3	13	84	2025-11-25	present	\N	\N	\N	\N
412	92	3	13	84	2025-11-25	present	\N	\N	\N	\N
413	93	3	13	84	2025-11-25	present	\N	\N	\N	\N
414	94	3	13	84	2025-11-25	present	\N	\N	\N	\N
415	95	3	13	84	2025-11-25	present	\N	\N	\N	\N
416	96	3	13	84	2025-11-25	present	\N	\N	\N	\N
417	97	3	13	84	2025-11-25	present	\N	\N	\N	\N
418	1	1	13	9	2025-11-25	absent	\N	\N	\N	\N
419	2	1	13	9	2025-11-25	present	\N	\N	\N	\N
420	3	1	13	9	2025-11-25	present	\N	\N	\N	\N
421	4	1	13	9	2025-11-25	present	\N	\N	\N	\N
422	5	1	13	9	2025-11-25	present	\N	\N	\N	\N
423	6	1	13	9	2025-11-25	present	\N	\N	\N	\N
424	7	1	13	9	2025-11-25	present	\N	\N	\N	\N
425	8	1	13	9	2025-11-25	present	\N	\N	\N	\N
426	9	1	13	9	2025-11-25	present	\N	\N	\N	\N
427	10	1	13	9	2025-11-25	present	\N	\N	\N	\N
428	11	1	13	9	2025-11-25	present	\N	\N	\N	\N
429	12	1	13	9	2025-11-25	present	\N	\N	\N	\N
430	13	1	13	9	2025-11-25	present	\N	\N	\N	\N
431	14	1	13	9	2025-11-25	present	\N	\N	\N	\N
432	15	1	13	9	2025-11-25	present	\N	\N	\N	\N
433	16	1	13	9	2025-11-25	present	\N	\N	\N	\N
434	17	1	13	9	2025-11-25	present	\N	\N	\N	\N
435	18	1	13	9	2025-11-25	present	\N	\N	\N	\N
436	19	1	13	9	2025-11-25	present	\N	\N	\N	\N
437	20	1	13	9	2025-11-25	present	\N	\N	\N	\N
438	21	1	13	9	2025-11-25	present	\N	\N	\N	\N
439	22	1	13	9	2025-11-25	present	\N	\N	\N	\N
440	23	1	13	9	2025-11-25	present	\N	\N	\N	\N
441	24	1	13	9	2025-11-25	present	\N	\N	\N	\N
442	25	1	13	9	2025-11-25	present	\N	\N	\N	\N
443	26	1	13	9	2025-11-25	present	\N	\N	\N	\N
444	27	1	13	9	2025-11-25	present	\N	\N	\N	\N
445	28	1	13	9	2025-11-25	present	\N	\N	\N	\N
446	29	1	13	9	2025-11-25	present	\N	\N	\N	\N
447	30	1	13	9	2025-11-25	present	\N	\N	\N	\N
448	31	1	13	9	2025-11-25	present	\N	\N	\N	\N
449	32	1	13	9	2025-11-25	present	\N	\N	\N	\N
450	33	1	13	9	2025-11-25	present	\N	\N	\N	\N
451	1	1	14	84	2025-11-26	absent	excused	sdsadasdas	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
452	2	1	14	84	2025-11-26	absent	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
453	3	1	14	84	2025-11-26	absent	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
454	4	1	14	84	2025-11-26	absent	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
455	5	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
456	6	1	14	84	2025-11-26	absent	excused	\N	2025-11-26 00:13:54.307272	2025-11-26 00:23:18.712532
457	7	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
458	8	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
459	9	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
460	10	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
461	11	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
462	12	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
463	13	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
464	14	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
465	15	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
466	16	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
467	17	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
468	18	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
469	19	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
470	20	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
471	21	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
472	22	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
473	23	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
474	24	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
475	25	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
476	26	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
477	27	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
478	28	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
479	29	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
480	30	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
481	31	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
482	32	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
483	33	1	14	84	2025-11-26	present	\N	\N	2025-11-26 00:13:54.307272	2025-11-26 00:18:52.387767
\.


--
-- TOC entry 3567 (class 0 OID 16417)
-- Dependencies: 220
-- Data for Name: period; Type: TABLE DATA; Schema: public; Owner: adminit
--

COPY public.period (id, period_num, class_id, teacher_id, start_time, end_time, created_at, day_of_week) FROM stdin;
4	2	\N	\N	08:00:00	08:45:00	2025-11-29 20:18:18.731384	0
3	1	\N	\N	07:05:00	07:55:00	2025-11-29 20:16:20.134865	0
10	7	\N	\N	12:00:00	13:00:00	2025-11-29 20:34:45.043807	0
11	8	\N	\N	00:00:00	04:00:00	2025-11-29 20:35:27.884375	0
12	3	\N	\N	17:00:00	18:00:00	2025-12-13 14:28:59.82	6
\.


--
-- TOC entry 3565 (class 0 OID 16402)
-- Dependencies: 218
-- Data for Name: school_class; Type: TABLE DATA; Schema: public; Owner: adminit
--

COPY public.school_class (id, name, teacher_id, created_at) FROM stdin;
6	10/5	\N	2025-11-28 07:21:06.064328
8	10/7	\N	2025-11-28 07:21:06.071029
9	10/8	\N	2025-11-28 07:21:06.073433
10	10/9	\N	2025-11-28 07:21:06.075131
11	11/1	\N	2025-11-28 07:21:06.076604
12	11/10	\N	2025-11-28 07:21:06.078655
13	11/2	\N	2025-11-28 07:21:06.080044
14	11/3	\N	2025-11-28 07:21:06.081365
15	11/4	\N	2025-11-28 07:21:06.084009
16	11/5	\N	2025-11-28 07:21:06.0857
17	11/6	\N	2025-11-28 07:21:06.087117
18	11/7	\N	2025-11-28 07:21:06.088419
19	11/8	\N	2025-11-28 07:21:06.089612
20	11/9	\N	2025-11-28 07:21:06.090782
21	12/1	\N	2025-11-28 07:21:06.091894
22	12/10	\N	2025-11-28 07:21:06.093233
23	12/2	\N	2025-11-28 07:21:06.09498
24	12/3	\N	2025-11-28 07:21:06.096256
25	12/4	\N	2025-11-28 07:21:06.09763
26	12/5	\N	2025-11-28 07:21:06.099673
27	12/6	\N	2025-11-28 07:21:06.101308
28	12/7	\N	2025-11-28 07:21:06.103476
29	12/8	\N	2025-11-28 07:21:06.105089
30	12/9	\N	2025-11-28 07:21:06.106377
5	10/4	\N	2025-11-28 07:21:06.062284
7	10/6	14	2025-11-28 07:21:06.067951
1	10/1	15	2025-11-28 07:21:06.030899
2	10/10	15	2025-11-28 07:21:06.055759
3	10/2	15	2025-11-28 07:21:06.057131
4	10/3	15	2025-11-28 07:21:06.060037
\.


--
-- TOC entry 3569 (class 0 OID 16437)
-- Dependencies: 222
-- Data for Name: student; Type: TABLE DATA; Schema: public; Owner: adminit
--

COPY public.student (id, name, roll_number, class_id, email, phone, created_at) FROM stdin;
345	نديم جان	30858601757	11	\N	70507054	2025-11-28 10:38:57.454576
340	محمد نيازى محمد وطفه	30976000023	11	\N	0	2025-11-28 10:38:57.453423
1	ابراهيم محمد ابراهيم زين سلامه	31081801003	1	\N	77406928	2025-11-28 10:38:57.340108
2	احمد حافظ محمد ابوطاهر محمدموسى	31005000101	1	\N	55449406	2025-11-28 10:38:57.342189
3	ازهرى محمد ازهرى الحاج العركى	31073600139	1	\N	55270454	2025-11-28 10:38:57.342927
4	اسامه عبدى نور محمود يكل	30970600047	1	\N	55753935	2025-11-28 10:38:57.343429
5	انس وائل مبروك محمد سلطان	31081805086	1	\N	30063083	2025-11-28 10:38:57.343867
6	بدر محمد خدا داد	31058600487	1	\N	55965131	2025-11-28 10:38:57.344397
7	جابر حمد جابر البريدى المرى	31063403003	1	\N	77771131	2025-11-28 10:38:57.344886
8	حمد جان زيب جول جان	31058600840	1	\N	70501600	2025-11-28 10:38:57.345238
9	حمد عبدالمنعم محسن اليهرى اليافعي	31088600074	1	\N	66547555	2025-11-28 10:38:57.34558
10	خالد على سعد خالد مقبل	31063402375	1	\N	51644440	2025-11-28 10:38:57.345954
11	خالد عماد عبدالكريم ناصر الكلدي	31188600250	1	\N	55055153	2025-11-28 10:38:57.346286
12	زايد سعيد متعب قحيز المرى	30763403362	1	\N	66766437	2025-11-28 10:38:57.346635
13	سحيم سالم محمد القمرا المرى	30863403148	1	\N	55364648	2025-11-28 10:38:57.346994
14	سعيد عبدالله ناصر عبدالله نوره	30963403118	1	\N	55634111	2025-11-28 10:38:57.347329
15	سلطان جابر حمد النابت المرى	31063400266	1	\N	55888608	2025-11-28 10:38:57.348406
16	صالح سالم صالح الربيط السنيد	30763404731	1	\N	55003385	2025-11-28 10:38:57.348745
17	صالح محمد صالح الغفران المرى	31063400047	1	\N	33330596	2025-11-28 10:38:57.34907
18	عبدالرحمن تاى الله محمد تاى الله العجب	30973600579	1	\N	66252657	2025-11-28 10:38:57.349389
19	عبدالرحمن محمد سعيد الغضيض المرى	31063403435	1	\N	55254133	2025-11-28 10:38:57.349714
20	عبدالله راشد حمد سالم العذبه	31063406223	1	\N	33333082	2025-11-28 10:38:57.350041
21	عبدالله محمد ابراهيم	31058600573	1	\N	70993355	2025-11-28 10:38:57.350366
22	علي محمد علي الجابر المري	30868200175	1	\N	77007794	2025-11-28 10:38:57.350686
23	فهد ابوبكر محمود دلول	30999900431	1	\N	66772239	2025-11-28 10:38:57.351006
24	مازن محمود فتحى محمد اسماعيل	31181803138	1	\N	70482215	2025-11-28 10:38:57.351319
25	مبارك راشد سعيد محمد النابت	30863400465	1	\N	70773884	2025-11-28 10:38:57.35163
26	محمد بخيت محمد المنخس المرى	31063402741	1	\N	55889608	2025-11-28 10:38:57.351976
27	محمد راشد محمد راشد المنخس	31063407484	1	\N	55844476	2025-11-28 10:38:57.352295
28	محمد عبدالله على ابوشارب المسعود	30963401946	1	\N	55823838	2025-11-28 10:38:57.352601
29	محمد ناصر سعيد خميس الغنبوصي	31051200100	1	\N	77379492	2025-11-28 10:38:57.352902
30	مروان محمد مانع الازوح	31088600555	1	\N	66589997	2025-11-28 10:38:57.353185
31	مشعل محمد صالح المري	31068200085	1	\N	66138885	2025-11-28 10:38:57.353462
32	ناصر محمد ناصر الغفرانى المرى	31063406125	1	\N	33187131	2025-11-28 10:38:57.353744
33	نايف خالد عمر محمد الجعيدى	31088600239	1	\N	55678972	2025-11-28 10:38:57.354043
34	ابراهيم محمد ابراهيم محمود ماضى	30999900345	2	\N	55837392	2025-11-28 10:38:57.354357
35	احمد محمد سليمان حوراني	31040002003	2	\N	70724889	2025-11-28 10:38:57.354673
36	انس الطاف حسين عبدالله	30905000070	2	\N	55405260	2025-11-28 10:38:57.355011
37	ايمن على العذاب	31076001160	2	\N	33689149	2025-11-28 10:38:57.355329
38	جواد محمد رياض نورباز	31058600680	2	\N	55837800	2025-11-28 10:38:57.355638
39	حمد سالم محسن عبدالله ملهيه	31063400341	2	\N	55099943	2025-11-28 10:38:57.355933
40	حمد مبخوت جابر حمد مسعود	31263400538	2	\N	66006641	2025-11-28 10:38:57.35624
41	راشد سعيد ناصر راشد المقارح	31163402057	2	\N	77066663	2025-11-28 10:38:57.356552
42	صالح حمد مبارك اليتيم المرى	30963400572	2	\N	55217298	2025-11-28 10:38:57.356872
43	عبدالرحمن محمد امام بخش صالح	31058600171	2	\N	55403403	2025-11-28 10:38:57.357189
44	عبدالله صالح محسن عبدالله ملهيه	31063407295	2	\N	50051333	2025-11-28 10:38:57.357509
45	عبدالله مبارك على سعيد السفران	31063405195	2	\N	55000630	2025-11-28 10:38:57.357843
46	على جابر على الربيط المرى	30763400588	2	\N	66769872	2025-11-28 10:38:57.358201
47	عمر محمد يوسف شير محمد	30958600045	2	\N	66681063	2025-11-28 10:38:57.358533
48	محمد ابراهيم محمد العمري	31040000970	2	\N	33307439	2025-11-28 10:38:57.358876
49	محمد احمد السيد محمود عبد الرحيم	31081805713	2	\N	55372961	2025-11-28 10:38:57.359205
50	محمد حمد سالم العفيفه المرى	31063400552	2	\N	55097272	2025-11-28 10:38:57.359538
51	محمد حمد سالم محمد المرى	31063404980	2	\N	55302223	2025-11-28 10:38:57.359891
52	محمد حمد على حمد الكربى	30963407526	2	\N	66904014	2025-11-28 10:38:57.360204
53	محمد سعيد صالح عبدالله الصوفى	30988600485	2	\N	55432342	2025-11-28 10:38:57.360519
54	محمد فخرى سعيد عيسى عزام	31099900392	2	\N	55568896	2025-11-28 10:38:57.360847
55	محمد مبخوت على سالم النجم	31063405897	2	\N	55521016	2025-11-28 10:38:57.361162
56	محمد مسفر محمد عبدالله السفران	31063406271	2	\N	55512380	2025-11-28 10:38:57.361497
57	مشعل محسن جابر فطيس المرى	31063407320	2	\N	55255997	2025-11-28 10:38:57.361819
58	ناصر عبدالله محمد عبدالله عفيفه	31063404607	2	\N	55144413	2025-11-28 10:38:57.362143
59	ناصر علي محمد الكربي	31088600259	2	\N	55290233	2025-11-28 10:38:57.362464
60	ناصر محمد سالم حمد هطيل	31063402675	2	\N	66555630	2025-11-28 10:38:57.362782
61	نايف محسن محمد الحسناء المرى	30763403592	2	\N	55894445	2025-11-28 10:38:57.363096
62	هادى عبدالله هادى محمد هادى	31063405798	2	\N	66871888	2025-11-28 10:38:57.363416
63	يوسف احمد زهدى عرفه	31040000517	2	\N	55873149	2025-11-28 10:38:57.363732
64	يوسف علوي سعيد عبدربه	30988600462	2	\N	55335619	2025-11-28 10:38:57.364057
65	يوسف محمود عبدالقادر محمد المكاوى	31081801969	2	\N	74485329	2025-11-28 10:38:57.364368
66	اياد خالد صاري	31076000838	3	\N	70110510	2025-11-28 10:38:57.364685
67	بسام نبيل ابوعلي	31176001160	3	\N	77140457	2025-11-28 10:38:57.365027
68	تميم حمد محمد القمرا المرى	31063403447	3	\N	55821778	2025-11-28 10:38:57.365346
69	تميم صالح حمد النابت المرى	30963404264	3	\N	55611806	2025-11-28 10:38:57.365887
70	حمد جارالله محمد البريدى المرى	31063402261	3	\N	33333035	2025-11-28 10:38:57.366209
341	محمد هاني الزعبي	30976001143	11	\N	55304477	2025-11-28 10:38:57.453631
71	حمد سعيد حمد الغفرانى المرى	31063400599	3	\N	55457779	2025-11-28 10:38:57.366537
72	حمد قابل بادشاه سان بادشاه	30958600241	3	\N	66050929	2025-11-28 10:38:57.366868
73	راشد ناصر راشد العوامى المرى	31063403902	3	\N	55558575	2025-11-28 10:38:57.367185
74	سالم سعد سالم الهولى النعيمى	31163400382	3	\N	55009229	2025-11-28 10:38:57.367505
75	سالم صالح سالم سعيد العيده	31063400564	3	\N	55095091	2025-11-28 10:38:57.367829
76	سعود سالم حمد النابت المرى	30963400006	3	\N	0	2025-11-28 10:38:57.368146
77	سعود سالم حمد على الكربى	31063407414	3	\N	33331188	2025-11-28 10:38:57.368474
78	سعيد حمد على راشد ملهيه	30863405319	3	\N	33111105	2025-11-28 10:38:57.368825
79	سلطان عمر	30858601721	3	\N	55370979	2025-11-28 10:38:57.369144
80	سليمان محسن عوض اليهرى اليافعى	31063405480	3	\N	55804678	2025-11-28 10:38:57.369456
81	عبدالرحمن على محمود طلبه عامر	30981804776	3	\N	0	2025-11-28 10:38:57.369783
82	عبدالله ايمن عبدالحميد محمد خضر	31081800707	3	\N	55256750	2025-11-28 10:38:57.37011
83	عبدالله راشد حمد على العذبى	31163403032	3	\N	55815222	2025-11-28 10:38:57.370426
84	عبدالله سعيد جابر البريدى المرى	31063403454	3	\N	70033363	2025-11-28 10:38:57.370762
85	عبدالله سعيد علي المري	30968200318	3	\N	66829019	2025-11-28 10:38:57.371111
86	عبدالله محمد حميدى سالم العذبه	31063401814	3	\N	66662970	2025-11-28 10:38:57.371455
87	على سالم محمد البريص المرى	31063405748	3	\N	55532252	2025-11-28 10:38:57.371971
88	محمد سالم راشد حمد صبيح	31063400653	3	\N	55734555	2025-11-28 10:38:57.372342
89	محمد عبدالهادى محمد سعيد عزب	31063406737	3	\N	77950505	2025-11-28 10:38:57.372659
90	محمد فريد عباس بشير	31073600912	3	\N	33677710	2025-11-28 10:38:57.372983
91	محمد ناصر السر ناصر	31173601238	3	\N	31372589	2025-11-28 10:38:57.373298
92	محمد هشام احمد محمد الجزار	31181802920	3	\N	77702314	2025-11-28 10:38:57.373612
93	محمد يوسف احمد هياجنه	31040001199	3	\N	33118520	2025-11-28 10:38:57.373949
94	مسفر فارس محمد ذفال الحبابى	31063402794	3	\N	55556815	2025-11-28 10:38:57.374279
95	مشهور عليان محمد صالح المري	30841400012	3	\N	55632222	2025-11-28 10:38:57.374622
96	ناصر ماجد سعد شالح الدوسرى	31063407901	3	\N	55556341	2025-11-28 10:38:57.37497
97	يوسف على بخيت البريدى المرى	31063405063	3	\N	71500700	2025-11-28 10:38:57.376121
98	جمال التهامي زروق	31078800455	4	\N	55579873	2025-11-28 10:38:57.376533
99	حمد منصور بلوج	31036400238	4	\N	55324454	2025-11-28 10:38:57.376864
100	زايد حميدى على الحميدى المقارح	31063403627	4	\N	55888985	2025-11-28 10:38:57.377177
101	سالم حمد جارالله الغفرانى المرى	31063403661	4	\N	55854221	2025-11-28 10:38:57.377498
102	سالم على منصر القايد الغياثين	30863401483	4	\N	55868881	2025-11-28 10:38:57.37782
103	شقران حمد راشد التويجر المرى	31063402533	4	\N	55125552	2025-11-28 10:38:57.378153
104	صالح محمد سعيد صالح ملهيه	31063407513	4	\N	70555585	2025-11-28 10:38:57.37847
105	عبدالرحمن حاتم محمد حسين السعدي	31088600609	4	\N	55665646	2025-11-28 10:38:57.37879
106	عبدالله بريك هادى محمد هادى	31063402647	4	\N	55547887	2025-11-28 10:38:57.379107
107	عبدالله راشد مبارك الجربوعى المرى	30563405474	4	\N	66049953	2025-11-28 10:38:57.379422
108	على احمد رسول	30958601479	4	\N	55868022	2025-11-28 10:38:57.37976
109	على احمد سالم مشاجل الكثيرى	30663402751	4	\N	55857756	2025-11-28 10:38:57.380074
110	على راشد على بعيهان النابت	31063404477	4	\N	50581777	2025-11-28 10:38:57.380393
111	على عبدالله على ابوشارب المسعود	30863401864	4	\N	55823838	2025-11-28 10:38:57.38072
112	عمر نورالدين الحريري	31176001193	4	\N	70456085	2025-11-28 10:38:57.38105
113	فهد محمد ناصر ال حارث اليامى	31063400740	4	\N	70999949	2025-11-28 10:38:57.381361
114	محمد حسين صالح محمد الشريف	31188600806	4	\N	31135300	2025-11-28 10:38:57.381677
115	محمد رفيق فرحان احمد دلول	30999900377	4	\N	77077026	2025-11-28 10:38:57.382154
116	محمد سعيد فهد الخديعه المرى	31063402114	4	\N	77577676	2025-11-28 10:38:57.382479
117	محمد عبدالله محمد مبارك النابت	31063400357	4	\N	55055167	2025-11-28 10:38:57.383049
118	محمد على حمد على مقارح	31063407421	4	\N	55111136	2025-11-28 10:38:57.383476
119	محمد على محمد نعيمى	31036400038	4	\N	55707052	2025-11-28 10:38:57.383809
120	محمد مبارك راشد مبارك الهاجرى	31063407867	4	\N	55504460	2025-11-28 10:38:57.384121
121	محمد ياسر ثابت عثمان السعدى	31088600411	4	\N	55777553	2025-11-28 10:38:57.384449
122	محمد ياسين محسن الصانع	31188600161	4	\N	77113732	2025-11-28 10:38:57.384774
123	مسعود خالد مسعود الحميدانى القحطانى	31063404502	4	\N	33333146	2025-11-28 10:38:57.385093
124	مصعب ابراهيم المهدى قناو	31043400065	4	\N	66787987	2025-11-28 10:38:57.385418
125	معتزبالله احمد صابر خليفه الديب	31081802818	4	\N	31301090	2025-11-28 10:38:57.385777
126	ناصر سالم ناصر المهرى	31068200149	4	\N	66564750	2025-11-28 10:38:57.386127
127	ناصر عبدالله حمد النابتى المرى	30763401692	4	\N	55128056	2025-11-28 10:38:57.386443
128	نواف ظافر محمد الهرمسى الهاجرى	31063403070	4	\N	66669510	2025-11-28 10:38:57.38679
129	يوسف عبدالعزيز محسن اليهري اليافعي	31088600184	4	\N	66818155	2025-11-28 10:38:57.387134
130	احمد عبدالله على العريض المرى	31063406374	5	\N	77777433	2025-11-28 10:38:57.387486
131	احمد محمد محمود	30747800073	5	\N	55401768	2025-11-28 10:38:57.387888
132	احمد وائل عثمان الحاج احمد	31073600821	5	\N	30105422	2025-11-28 10:38:57.388223
133	جابر صالح على السنارى الجحيش	31063400807	5	\N	59926600	2025-11-28 10:38:57.388553
134	جابر هادى جابر البريدى المرى	31063400879	5	\N	77706626	2025-11-28 10:38:57.388881
135	جارالله سعيد حمد سالمين المرى	31063407461	5	\N	66513333	2025-11-28 10:38:57.389193
136	جاسم حمد راشد سالم المرى	31063406998	5	\N	51111503	2025-11-28 10:38:57.389617
137	حمد محمد حمد عوير القاشوطى	31063406396	5	\N	55387766	2025-11-28 10:38:57.38997
138	خالد سعيد عبدالهادى البريص المرى	31063404286	5	\N	77443477	2025-11-28 10:38:57.390328
139	راشد جارالله راشد المسعود العذبه	31063405939	5	\N	30282828	2025-11-28 10:38:57.390648
140	سالم حمد سالم الكاموخه المرى	31063404265	5	\N	55804445	2025-11-28 10:38:57.390981
141	سالم سلطان سالم راشد العلوي	31051200334	5	\N	66310474	2025-11-28 10:38:57.391328
142	سعيد ناصر سعيد المريزيق المرى	30863403920	5	\N	55300313	2025-11-28 10:38:57.391656
143	عايض راشد خجيم راشد العذبه	31063405954	5	\N	66154431	2025-11-28 10:38:57.391986
144	عبدالرحمن جهاد عمر عوض بانى	31088600309	5	\N	55358354	2025-11-28 10:38:57.392374
145	عبدالرحمن عبدالعزيز المهيني	31076001164	5	\N	55144467	2025-11-28 10:38:57.392883
146	عبدالرحمن محمد ناجى عبدالمنعم ناجى	30981803982	5	\N	55892140	2025-11-28 10:38:57.393454
147	عبدالله راشد سعيد محمد النابت	31063403895	5	\N	55472217	2025-11-28 10:38:57.393976
148	عبدالله علي هوتي	31058600122	5	\N	55035884	2025-11-28 10:38:57.39437
149	عبدالله محمد عبدالله البريدى المرى	31063402902	5	\N	55506001	2025-11-28 10:38:57.394697
150	فهد محمد حمد الشريف الكربى	31063404295	5	\N	55828551	2025-11-28 10:38:57.395031
151	فيصل ساجد عبدالله البلوشي	31051200141	5	\N	55982393	2025-11-28 10:38:57.395353
152	مبارك حمد سالم حمد المرى	30563401214	5	\N	51200084	2025-11-28 10:38:57.395673
153	محمد حسين على الغفرانى المرى	31063404721	5	\N	55523244	2025-11-28 10:38:57.395998
154	محمد حمد راشد طفله الفهيده	30963401015	5	\N	66995599	2025-11-28 10:38:57.396325
155	محمد سعيد سالم سعيد بن نوره	31163402928	5	\N	55222527	2025-11-28 10:38:57.396649
156	محمد سليم على سالم المرى	31163401768	5	\N	55365000	2025-11-28 10:38:57.396997
157	محمد عبدالعزيز المهيني	31076001165	5	\N	55144467	2025-11-28 10:38:57.39737
158	ناصر على قائد على مشرح	31188600208	5	\N	55565795	2025-11-28 10:38:57.398098
159	ناصر مبارك محمد النابت المرى	30963405834	5	\N	55551430	2025-11-28 10:38:57.398683
160	يوسف العوضي سعيد معتيق مهومد	31088600602	5	\N	55055705	2025-11-28 10:38:57.399036
161	احمد عبدالرحيم الله داتا	30858600606	6	\N	55213472	2025-11-28 10:38:57.399395
162	احمد محمد العبيد بلوله احمد	31073600331	6	\N	66931354	2025-11-28 10:38:57.399697
163	افضل الدين مزاج الدين	30958600387	6	\N	66686786	2025-11-28 10:38:57.399954
164	جابر على حمد حسين الجرحب	31063402821	6	\N	55289916	2025-11-28 10:38:57.400185
165	حسن على سعد السلمان القحطاني	31063403018	6	\N	55244235	2025-11-28 10:38:57.400402
166	حمد تويم حمد المنخس المرى	30963403196	6	\N	55421515	2025-11-28 10:38:57.400618
167	حمد سعيد راشد سعيد الغرينيق	31063406165	6	\N	55055539	2025-11-28 10:38:57.400845
168	حمد عبدالهادى حمد الدحابيب المرى	30863405376	6	\N	66998688	2025-11-28 10:38:57.401063
169	حمدان سعيد محسن حمد ابوصلعه	30963405089	6	\N	66777173	2025-11-28 10:38:57.40129
170	خالد فيصل الحاج	31076000985	6	\N	55047939	2025-11-28 10:38:57.401502
171	سعيد شاهد محمد شاهد	30905000192	6	\N	55946830	2025-11-28 10:38:57.40171
172	سعيد عبدالله حمد محمد ابوصلعه	30763404048	6	\N	50276902	2025-11-28 10:38:57.401926
173	سعيد عبدالهادى سعيد البريص المرى	31063402232	6	\N	55444553	2025-11-28 10:38:57.40213
174	سعيد محمد سعيد على المرى	31063405595	6	\N	0	2025-11-28 10:38:57.402336
175	سلطان خالد احمد حسن سعد	31063402805	6	\N	55885854	2025-11-28 10:38:57.40254
176	عبدالرحمن ادريس اسفداي	31008000025	6	\N	55024254	2025-11-28 10:38:57.402751
177	عبدالرحمن سعيد تويم كليفيخ المنخس	31063403762	6	\N	70777180	2025-11-28 10:38:57.402953
178	عبدالله حمد على صالح العذبه	31063401388	6	\N	55711141	2025-11-28 10:38:57.403155
179	عبدالله شاهد ابراهيم ادم	31058600366	6	\N	55019199	2025-11-28 10:38:57.404015
180	عبدالله محمد عبدالله البحيح المرى	31063404340	6	\N	66664555	2025-11-28 10:38:57.404294
181	على جارالله محمد ال بريد المرى	31063406846	6	\N	55715090	2025-11-28 10:38:57.40453
182	على عبدالله ناصر هطيل المرى	30963403696	6	\N	66621912	2025-11-28 10:38:57.404772
183	محمد جابر حمد ال مسعود المرى	31063406300	6	\N	33330524	2025-11-28 10:38:57.405027
184	محمد حسن عبدالباسط	31058601189	6	\N	30130195	2025-11-28 10:38:57.405361
185	محمد راشد سالم محمد الاسود	31063404593	6	\N	55151474	2025-11-28 10:38:57.405711
186	محمد صالح سالم الحول المرى	31163400076	6	\N	55697918	2025-11-28 10:38:57.406025
187	محمد صالح محمد الغفرانى المرى	31063406912	6	\N	55650404	2025-11-28 10:38:57.40635
188	محمد عبدالله محمد عبدالله السفران	31063403646	6	\N	66666675	2025-11-28 10:38:57.407683
189	منيب ناصف مختار عبدالقادر نصر	31073600684	6	\N	55483256	2025-11-28 10:38:57.408468
190	ناصر مسفر عبدالله سفران السفران	31063406641	6	\N	55064506	2025-11-28 10:38:57.409125
191	نايف مسعود بطحان عضيب المرى	31063407219	6	\N	55568500	2025-11-28 10:38:57.41005
192	يحيى رشاد حسن احمد عبادي	31088600737	6	\N	31091119	2025-11-28 10:38:57.410512
193	ابراهيم محمد الجاجه	31084000344	7	\N	55541973	2025-11-28 10:38:57.41086
194	ابوبكر سفروف	30976200004	7	\N	50335849	2025-11-28 10:38:57.411122
195	بشار أحمد ابراهيم الزعارير	31040001829	7	\N	33552630	2025-11-28 10:38:57.411357
196	بلال محمد حسين محمد يوسف	30958600339	7	\N	55299784	2025-11-28 10:38:57.411587
197	حسين سالم سعيد محمد العيده	31063401557	7	\N	55561036	2025-11-28 10:38:57.411826
198	حسين محمد حسين سعيد السفران	31063405871	7	\N	77555517	2025-11-28 10:38:57.412049
199	حمد صالح جابر محمد شقفان	31063404179	7	\N	55374444	2025-11-28 10:38:57.412285
200	حمد عبدالله عبداللاه عبده	31088600260	7	\N	55959604	2025-11-28 10:38:57.41257
201	حمد ناصر عبدالله الطرابيل البريدى	30763406418	7	\N	66626211	2025-11-28 10:38:57.412876
202	خالد اسامه شريف فياض الحلوح	31040000675	7	\N	66890003	2025-11-28 10:38:57.413174
203	خالد دغش سالم الجربوعى المرى	31063401899	7	\N	77772128	2025-11-28 10:38:57.41355
204	خليفه علي زين عبدالناصر	31088600650	7	\N	33443337	2025-11-28 10:38:57.413838
205	راشد هادى محمد الزبدان المرى	31063406718	7	\N	55556634	2025-11-28 10:38:57.414073
206	سالم محمد فهيد المكسور النابت	30563406114	7	\N	55780353	2025-11-28 10:38:57.414293
207	سلطان رشيد خان جول جنان	30858600661	7	\N	77889559	2025-11-28 10:38:57.414505
208	سيد هجيف	30905000242	7	\N	55693403	2025-11-28 10:38:57.414715
209	سيف سلطان فيصل المسافره الهاجرى	31063407863	7	\N	55049831	2025-11-28 10:38:57.414943
210	ظافر مبارك ظافر محمد القحطانى	31063406128	7	\N	55373377	2025-11-28 10:38:57.415172
211	عادل محمد اصغر	30958601062	7	\N	55361137	2025-11-28 10:38:57.415383
212	عبدالرحمن انور عبدالله الدوسرى	30936800099	7	\N	55729360	2025-11-28 10:38:57.415591
213	عبدالعزيز جابر صالح ال سنيد المرى	31063405833	7	\N	66625553	2025-11-28 10:38:57.415815
214	عبدالله احمد عبدالله	31047800009	7	\N	55331302	2025-11-28 10:38:57.416026
215	عبدالله سفران محمد عبدالله السفران	31063403538	7	\N	55551590	2025-11-28 10:38:57.416234
216	على تركى على الحنيتم المرى	31063403101	7	\N	66855556	2025-11-28 10:38:57.416441
217	على محمد على النشيرا المرى	31063407509	7	\N	55099600	2025-11-28 10:38:57.416647
218	فهد راشد فهيد الخديعه المرى	31063401784	7	\N	50888028	2025-11-28 10:38:57.416866
219	فهد محمد صالح المسعود العذبة	31063407466	7	\N	55011722	2025-11-28 10:38:57.417077
220	مبارك حمد محمد مبارك الجهويل	31063401123	7	\N	55894545	2025-11-28 10:38:57.417304
221	مبارك صالح مبارك محمد الكربي	31188600060	7	\N	50357557	2025-11-28 10:38:57.41751
222	متعب حمد متعب قحيز المرى	31063405770	7	\N	55038883	2025-11-28 10:38:57.417714
223	محمد جابر على الربيط المرى	31063405578	7	\N	55170155	2025-11-28 10:38:57.417934
224	محمد مبارك سعيد حمد جميله	31063403501	7	\N	70555599	2025-11-28 10:38:57.418142
225	مشعل سعيد حمد المهري	30968200106	7	\N	55128114	2025-11-28 10:38:57.418346
226	حمد جبران سعد على الحبابى	31063401385	8	\N	55596741	2025-11-28 10:38:57.418549
227	حمد صالح عبدالله الاحول الجحيش	31163400648	8	\N	33332330	2025-11-28 10:38:57.418768
228	حمد محمد على راشد حمد	31063403394	8	\N	55888598	2025-11-28 10:38:57.418975
229	خالد متعب على العريض المرى	31063405679	8	\N	55000577	2025-11-28 10:38:57.419178
230	راشد حمد راشد التويجر المرى	30963400366	8	\N	55125552	2025-11-28 10:38:57.419398
231	زيد عبدالله محمد نديله المرى	31063406003	8	\N	0	2025-11-28 10:38:57.419603
232	سالم عوض سالم هادى العجمى	31263402861	8	\N	55400075	2025-11-28 10:38:57.419821
233	سامى عبدالكريم لاهى السعدى	30851200260	8	\N	77555961	2025-11-28 10:38:57.420027
234	سعد رحمن	30858601752	8	\N	55095107	2025-11-28 10:38:57.420231
235	سعد عيدروس سالم احمد الحامد	31163401014	8	\N	66244806	2025-11-28 10:38:57.420437
236	سعيد جمعه سعيد ادريس	30908000030	8	\N	55767367	2025-11-28 10:38:57.420645
237	سعيد راشد عبدالله ابوشلنتحه المرى	30963404634	8	\N	55480004	2025-11-28 10:38:57.420865
238	سلطان على محمد على المرى	31063400308	8	\N	55155981	2025-11-28 10:38:57.421072
239	طه عمرو طه محمد موسى	30973600842	8	\N	55891378	2025-11-28 10:38:57.421277
240	عبدالرحمن حاتم عبدالكريم ناصر الكلدي	31088600366	8	\N	55541997	2025-11-28 10:38:57.421477
241	عبدالرحمن راشد حمد سالم العذبه	31063406224	8	\N	33333082	2025-11-28 10:38:57.421692
242	عبدالرحمن محمد اسماعيل	30858601078	8	\N	33444849	2025-11-28 10:38:57.421904
243	عبدالعزيز محمد زكريا صديق	31081800369	8	\N	50525799	2025-11-28 10:38:57.422108
244	عبدالله راشد سالم راشد ابوشارب	31063407271	8	\N	55856667	2025-11-28 10:38:57.422311
245	عبدالله محمد هادي القحطاني	31068200169	8	\N	70705527	2025-11-28 10:38:57.422513
246	على حمد على جرحب المرى	31063406705	8	\N	0	2025-11-28 10:38:57.422716
247	على حمد على حمد ابوصلعه	31163404924	8	\N	55688832	2025-11-28 10:38:57.422932
248	على طالب على دهمان المرى	31063405488	8	\N	55161611	2025-11-28 10:38:57.423133
249	عمر على عبدالله صالح العجى	31088600392	8	\N	55317311	2025-11-28 10:38:57.423401
250	عمر مهند عبدالكريم ابوخيران	31040001379	8	\N	39955558	2025-11-28 10:38:57.423708
251	فهد محمد راشد ال سنيد المرى	31163400372	8	\N	66662188	2025-11-28 10:38:57.424073
252	ماهر بابكر النور عبدالله	31073600707	8	\N	55601044	2025-11-28 10:38:57.424404
253	محمد احمد محمد عبدالله كده	39959747269	8	\N	55255519	2025-11-28 10:38:57.424751
254	محمد جابر سالم جابر مشعاب	31063400851	8	\N	55844788	2025-11-28 10:38:57.425101
255	محمد على محمد عبدالله السفران	31063403547	8	\N	55008788	2025-11-28 10:38:57.425448
256	نايف على محمد على المرى	31063400305	8	\N	55155981	2025-11-28 10:38:57.42585
257	اسامه ولي خان ميرسيد	30958600869	9	\N	30705665	2025-11-28 10:38:57.426502
258	البودير سليمان حسن ابكر	31014800005	9	\N	55433450	2025-11-28 10:38:57.427011
259	العز سليمان حسن	31014800004	9	\N	31305137	2025-11-28 10:38:57.427401
260	أيوب محمد بن عياد	30978800471	9	\N	50433001	2025-11-28 10:38:57.427721
261	جابر صالح على المطوع المرى	30963402943	9	\N	55853909	2025-11-28 10:38:57.428699
262	جارالله حمد جارالله المكسور النابت	31063407310	9	\N	55070529	2025-11-28 10:38:57.429006
263	جاسم محمد هادى الجربوعى المرى	31063404462	9	\N	55801645	2025-11-28 10:38:57.429323
264	حسن بنجشنبه بلوجى	30958601011	9	\N	55965559	2025-11-28 10:38:57.429561
265	حمد مبارك راشد محمد العاوى	30863400269	9	\N	66050550	2025-11-28 10:38:57.429795
266	خالد عبدالرحمن عبدالله عمر	30970600039	9	\N	77917115	2025-11-28 10:38:57.430107
267	خليفه راشد محمد حمد شاجع	31063402767	9	\N	55394736	2025-11-28 10:38:57.430362
268	راشد سعيد على راشد الاصم	30863400087	9	\N	70910000	2025-11-28 10:38:57.430593
269	راشد عبدالله راشد لسود المرى	31063407325	9	\N	59922229	2025-11-28 10:38:57.430833
270	سعد زيدان سعد الشمري	31168200061	9	\N	66661914	2025-11-28 10:38:57.431047
271	سعيد بخيت سعيد البريدى المرى	30963403675	9	\N	55333676	2025-11-28 10:38:57.431318
272	سعيد عبدالله حمد سعيد ابوشارب	31063402970	9	\N	66599939	2025-11-28 10:38:57.431546
273	طارق على اكبر امير حمزه	30905000164	9	\N	55506181	2025-11-28 10:38:57.431767
274	عبد العزيز عبد المجيد	30979200167	9	\N	55414340	2025-11-28 10:38:57.431982
275	عبدالرحمن محمد احمد احمد	30873600750	9	\N	66061377	2025-11-28 10:38:57.432196
276	عبدالرحمن ناظم بيك فرخوف	30976200002	9	\N	55963727	2025-11-28 10:38:57.432416
277	عبدالعزيز خلف وادى مسرهد الشمرى	31063405185	9	\N	55444010	2025-11-28 10:38:57.432623
278	عبدالعزيز عبدالقيوم أمام بخش	31051200168	9	\N	77707898	2025-11-28 10:38:57.432849
279	عبدالله راشد عبدالله ابوشلنتحه المرى	30463403291	9	\N	55480004	2025-11-28 10:38:57.433061
280	عبدالله علي قائد سيف	31088600597	9	\N	70098701	2025-11-28 10:38:57.433275
281	عثمان خالد عثمان عبدالله بالعرج	31088600022	9	\N	55175902	2025-11-28 10:38:57.433498
282	على سالم مبخوت سالم المرى	31063407437	9	\N	55280887	2025-11-28 10:38:57.433722
283	فهد محمد جاسم	31058601698	9	\N	77851578	2025-11-28 10:38:57.433958
284	محمد جاسم محمد مرزوقي فر	31036400078	9	\N	55675674	2025-11-28 10:38:57.434166
285	محمد سعيد صالح على الحديد	30963406537	9	\N	66000916	2025-11-28 10:38:57.434371
286	محمد محمد فياض امان جول	31058600224	9	\N	31555017	2025-11-28 10:38:57.434577
287	مشعل حمد سعيد ابوطحين المرى	30963406123	9	\N	55627898	2025-11-28 10:38:57.434793
288	احمد محمد مبارك اسماعيل الجاسم	30663401769	10	\N	0	2025-11-28 10:38:57.435
289	اسامه عماد صالح اليهري	30988600651	10	\N	30664777	2025-11-28 10:38:57.435209
290	جاسم حمد بداح محمد الهاجرى	31063403034	10	\N	33144492	2025-11-28 10:38:57.43541
291	حمد سالم على الجربوعى المرى	30963400183	10	\N	55824581	2025-11-28 10:38:57.435615
292	حمد سعيد حمد ابوسطوه الهاجرى	31163404039	10	\N	55511828	2025-11-28 10:38:57.435846
293	حمد مبارك حمد سفران المرى	31063407030	10	\N	55003386	2025-11-28 10:38:57.437919
294	راشد ناصر سعيد المريزيق المرى	31063407663	10	\N	55300313	2025-11-28 10:38:57.438336
295	سالم محمد صالح الرومى النابت	30963401639	10	\N	77555568	2025-11-28 10:38:57.438574
296	سعد محمد سالم الهولى النعيمى	30863404307	10	\N	66169464	2025-11-28 10:38:57.438818
297	سعيد جابر سعيد سالم مسعود	31063407659	10	\N	55338883	2025-11-28 10:38:57.439042
298	صالح حمد محمد النابت المرى	31063401851	10	\N	55959301	2025-11-28 10:38:57.439262
299	طلال عبيد راشد المسعود العذبه	31063403281	10	\N	55887796	2025-11-28 10:38:57.439478
300	عاصم حميد محمد	30758600788	10	\N	66622364	2025-11-28 10:38:57.439714
301	عبدالرحمن حمود عبدربه محمد حسين	30988600785	10	\N	31404006	2025-11-28 10:38:57.440821
302	عبدالرحمن سليمان حسين ال نسيم القحطانى	31063402890	10	\N	55858647	2025-11-28 10:38:57.441342
303	عبدالرحمن محمد حنيف حاجى عبدالحكيم	30858600697	10	\N	30644228	2025-11-28 10:38:57.441754
304	عبدالله جابر سعيد جابر عفيفه	31063401880	10	\N	55821000	2025-11-28 10:38:57.44304
305	عبدالله عصام الدين احمد محمود ماضى	31099900428	10	\N	55809094	2025-11-28 10:38:57.443888
306	على راشد على جرحب المرى	31063405907	10	\N	55840501	2025-11-28 10:38:57.444382
307	على سعيد عبدالله محمد السنارى	31063400224	10	\N	33796903	2025-11-28 10:38:57.444824
308	على ناصر محمد جابر المري	31078400030	10	\N	39925979	2025-11-28 10:38:57.445115
309	فهد صالح طالب صالح العذبه	31163401115	10	\N	33555999	2025-11-28 10:38:57.445384
310	فهد ميراصغر لال مين شاه	30863407472	10	\N	66667367	2025-11-28 10:38:57.445645
311	فهدالدين منهاج الدين حاجى جمال الدين	31058600012	10	\N	77677333	2025-11-28 10:38:57.445896
312	فيصل عبدالله حمد محمد الزكيبا	30963405462	10	\N	55880353	2025-11-28 10:38:57.44613
313	مبارك سالم على ال سفران المرى	30963404771	10	\N	55881090	2025-11-28 10:38:57.446366
314	محمد بروهي صالح محمد	30958601953	10	\N	66565638	2025-11-28 10:38:57.446653
315	محمد راشد سعيد محمد الزكيبا	31063407506	10	\N	74430008	2025-11-28 10:38:57.447069
316	محمد عبدالرحيم عبدالله عبدالرحيم درار	30873600692	10	\N	55327127	2025-11-28 10:38:57.447342
317	محمد عبدالمنعم محسن اليهرى اليافعى	31188600314	10	\N	66547555	2025-11-28 10:38:57.44758
318	ناصر حمد راشد العوامى المرى	31063401220	10	\N	55557515	2025-11-28 10:38:57.447824
319	احمد حسنى محمود عبدالمجيد احمد	31081801545	11	\N	77347929	2025-11-28 10:38:57.448045
320	احمد عبدالرحمن محمد عبدالمولى زيد	31081802983	11	\N	33205564	2025-11-28 10:38:57.44828
321	احمد محمد جاسم	30758601584	11	\N	30801064	2025-11-28 10:38:57.448495
322	احمد هاني الزعبي	30976001144	11	\N	55304477	2025-11-28 10:38:57.448708
323	اياد محمد طريف عبدالمنعم اسماعيل	31081804144	11	\N	70999945	2025-11-28 10:38:57.448935
324	حمد احمد عنفوص	30976001062	11	\N	66330412	2025-11-28 10:38:57.449149
325	رشاد عبدالله رشاد عبدالله مهنا	30999900287	11	\N	55526223	2025-11-28 10:38:57.449357
326	زياد علاءالدين فتحى امين خليل	30973600882	11	\N	55379381	2025-11-28 10:38:57.449687
327	زياد محمد عباس العريفي	30988600631	11	\N	50023808	2025-11-28 10:38:57.449927
328	صالح حمد صالح العطان المرى	30963406998	11	\N	33334864	2025-11-28 10:38:57.450146
329	عبدالرحمن نزال برغوث	30876000964	11	\N	66507181	2025-11-28 10:38:57.450361
330	عبدالله على عويض الصقور المرى	31063404542	11	\N	66331027	2025-11-28 10:38:57.450572
331	عبدالهادى صالح عبدالهادى نديل الكربى	30963404728	11	\N	60067888	2025-11-28 10:38:57.450795
332	عبدالوهاب كوراني	31079200202	11	\N	60003883	2025-11-28 10:38:57.451628
333	على محمد على سالم العذبه	30963406631	11	\N	30007077	2025-11-28 10:38:57.451869
334	عمر ايمن عيد عبدالعظيم عبدالحليم	30981802837	11	\N	30032775	2025-11-28 10:38:57.452088
335	عمر عبدالرحمن محمد عبدالمولى زيد	30881803075	11	\N	33205564	2025-11-28 10:38:57.4523
336	عمر معتصم عصام الريماوي	31040001053	11	\N	33970739	2025-11-28 10:38:57.45251
337	محمد احسان الحق محمد قيس الرياحي	31078800367	11	\N	55387525	2025-11-28 10:38:57.452718
338	محمد احمد مصطفى عبدالرحمن	30642200131	11	\N	55817792	2025-11-28 10:38:57.452998
339	محمد عصام مصطفى الحسن احمد	31073600377	11	\N	55388410	2025-11-28 10:38:57.45321
342	محمدالفاتح خالد محمد محمود	30940001294	11	\N	31140291	2025-11-28 10:38:57.453865
343	محمود رياض حسن عجاج	30976000238	11	\N	77106679	2025-11-28 10:38:57.454086
344	ناصر احمد عواد حميده العماش	30904800047	11	\N	55288422	2025-11-28 10:38:57.454326
346	يحيى محمد الصالح السليمان	30976000025	11	\N	55286740	2025-11-28 10:38:57.454822
347	يوسف ماهر محمد عامودى	30940001191	11	\N	50376717	2025-11-28 10:38:57.455061
348	يونس خان محمد سهراب بلوش	30958600279	11	\N	55634254	2025-11-28 10:38:57.455274
349	بندر على حمد جابر المنخس	30763403106	12	\N	30232303	2025-11-28 10:38:57.455509
350	جارالله سالم عبدالله ال نابت المرى	30963400526	12	\N	55491210	2025-11-28 10:38:57.455727
351	حمد جابر على الربيط المرى	30963404203	12	\N	66769872	2025-11-28 10:38:57.455973
352	حمدان سالم على دوحه القوز	30963402396	12	\N	55755500	2025-11-28 10:38:57.456187
353	حمدان سعيد حمد سالمين المرى	30963400397	12	\N	66513333	2025-11-28 10:38:57.456432
354	خالد على طالب شفيع المرى	30963400280	12	\N	55757088	2025-11-28 10:38:57.456694
355	خالد محمد صالح مانعه المرى	30963403895	12	\N	55122236	2025-11-28 10:38:57.457042
356	سالم ناصر جارالله الابهق المرى	30863406944	12	\N	55450005	2025-11-28 10:38:57.457386
357	سعيد على زايد كروز المرى	30963401570	12	\N	55481333	2025-11-28 10:38:57.457746
358	عبدالرحمن بهاءالدين ابراهيم محمد اهل	30999900035	12	\N	55380551	2025-11-28 10:38:57.458094
359	عبدالرحمن ناصر جابر البريدى المرى	30663404756	12	\N	55557433	2025-11-28 10:38:57.458444
360	عبدالله جابر حمد عبدالله الحنزاب	30963400622	12	\N	55548111	2025-11-28 10:38:57.458794
361	عبدالله ناصر يوسف	30558600092	12	\N	55416491	2025-11-28 10:38:57.459214
362	عزام مهدى على مهدى القحطانى	30963404377	12	\N	0	2025-11-28 10:38:57.45985
363	على حمد احمد محمد الانصارى	30963404430	12	\N	55532262	2025-11-28 10:38:57.460353
364	على سالم على سالم العذبى	30963403227	12	\N	55007170	2025-11-28 10:38:57.460685
365	على سالم فهيد سالم دلوان	30863400771	12	\N	55895577	2025-11-28 10:38:57.461034
366	على صالح محمد صالح الجرحب	30963400703	12	\N	55533465	2025-11-28 10:38:57.461272
367	على محمد حمد ال جهويل المرى	30963401655	12	\N	55537551	2025-11-28 10:38:57.4615
368	على محمد حمد صالح الشرقى	30663404700	12	\N	55046116	2025-11-28 10:38:57.461725
369	على محمد راشد على المرى	30863405813	12	\N	55164693	2025-11-28 10:38:57.461972
370	على محمد هادى على البريدى	30963406790	12	\N	55989873	2025-11-28 10:38:57.462205
371	فهد حمد سعيد العذبى المرى	31063405504	12	\N	33333652	2025-11-28 10:38:57.462521
372	مبخوت محمد ناصر البحيح المرى	30763402508	12	\N	55022217	2025-11-28 10:38:57.462774
373	مترك جبران سعد على الحبابى	30863404223	12	\N	71710181	2025-11-28 10:38:57.463117
374	محمد سعيد سالم ابوضحا القوز	30863403093	12	\N	0	2025-11-28 10:38:57.463578
375	محمد على طالب شفيع المرى	30963400281	12	\N	55757088	2025-11-28 10:38:57.463984
376	محمد على محمد على الجرحب	30963406138	12	\N	55505852	2025-11-28 10:38:57.464364
377	محمد ناصر محمد جابر المري	30978400028	12	\N	50985791	2025-11-28 10:38:57.464727
378	ناصر جابر هادى على البريدى	31063401714	12	\N	77707222	2025-11-28 10:38:57.465103
379	ناصر سعيد حمد سعيد العيده	31063400711	12	\N	55070047	2025-11-28 10:38:57.465471
380	احمد علي احمد علي القضيب	30988600678	13	\N	66474811	2025-11-28 10:38:57.465824
381	البراء محمد هيثم عبده محسن	30888600614	13	\N	33974684	2025-11-28 10:38:57.466197
382	ايمن ادم همد محمدعلي	30973601133	13	\N	77577382	2025-11-28 10:38:57.466547
383	خالد محمد اقبال سيد بلوشي	30858600775	13	\N	55755453	2025-11-28 10:38:57.466955
384	راشد عبدالكريم حافظ فضل كريم	30958600187	13	\N	55514750	2025-11-28 10:38:57.467394
385	زايد حمد هادى الجربوعى المرى	30963407140	13	\N	55228841	2025-11-28 10:38:57.467792
386	سعود على راشد الادهم المرى	30963407511	13	\N	55542894	2025-11-28 10:38:57.468162
387	سعيد حمد على النابت المرى	30963405611	13	\N	55070606	2025-11-28 10:38:57.468507
388	عادل عبدالحق باقى جول	30758600538	13	\N	77788907	2025-11-28 10:38:57.468844
389	عبد الحكم شريف احمد محمود محمد	30981804744	13	\N	30602605	2025-11-28 10:38:57.469168
390	عبدالرحمن عمر يحيى الموسطى اليافعى	30963406623	13	\N	30150013	2025-11-28 10:38:57.469847
391	عبدالعزيز عبدالله محمد دريميح المرى	30963400431	13	\N	55549300	2025-11-28 10:38:57.470188
392	عبدالله سالم عبدالله مبارك بن نوره	31063400918	13	\N	55572266	2025-11-28 10:38:57.470519
393	عبدالله ناظم بيك فرخوف	30876200004	13	\N	74743921	2025-11-28 10:38:57.470878
394	عبدالهادى محمد عبدالهادى نديل الكربى	30963403311	13	\N	66050580	2025-11-28 10:38:57.471241
395	على عبدالقادر علي البرعى	31073600228	13	\N	55364066	2025-11-28 10:38:57.471576
396	على محمد على ناصر العنسى	30940000354	13	\N	55310080	2025-11-28 10:38:57.471925
397	علي موسى علي القرارعه	30940001487	13	\N	50083842	2025-11-28 10:38:57.472264
398	عمار احمد يوسف جابر نصر	30999900426	13	\N	55827438	2025-11-28 10:38:57.472603
399	عمر احمد زبير عبداللة الدينى	30888600380	13	\N	66683319	2025-11-28 10:38:57.472943
400	عمر نبيل محمد مصطفى النمرات	30840000688	13	\N	55229427	2025-11-28 10:38:57.473272
401	فهد رحمن	30758601665	13	\N	55095107	2025-11-28 10:38:57.473605
402	محمد خليفه عبدالله ناجى العبدالله	31063400065	13	\N	55181871	2025-11-28 10:38:57.473946
403	محمد صلاح عبدربه	30988600500	13	\N	55322055	2025-11-28 10:38:57.474282
404	محمد ظافر فرج ال راشد القحطانى	30963405900	13	\N	70065719	2025-11-28 10:38:57.474669
405	محمد عبدالقادر علي البرعى ابراهيم	30873600587	13	\N	55364066	2025-11-28 10:38:57.475059
406	محمد عبدالله صالح عفيشه	30988600237	13	\N	77721187	2025-11-28 10:38:57.47552
407	محمد نعمت الله خيستا محمد بادشاه	30858600287	13	\N	33561290	2025-11-28 10:38:57.475914
408	مشعل هلال حسن خلف العماش	30963404353	13	\N	55807437	2025-11-28 10:38:57.47635
409	معاذ حسين نعسان	30976000883	13	\N	30508600	2025-11-28 10:38:57.476982
410	نايف على سالم صبيح السنيد	30963402206	13	\N	66662706	2025-11-28 10:38:57.477282
411	هادى احمد مصطفى عبدالرحمن	30842200061	13	\N	55817792	2025-11-28 10:38:57.477615
412	احمد عثمان محمد عزالدين النور	30973600461	14	\N	55329314	2025-11-28 10:38:57.47872
413	احمد مصطفى احمد قسم السيدمحمد	30773600574	14	\N	55593596	2025-11-28 10:38:57.479282
414	المنذر يوسف حامد يوسف	30973600507	14	\N	55124880	2025-11-28 10:38:57.479955
415	جهاد محسن محمد صوان	30940001809	14	\N	71003113	2025-11-28 10:38:57.480942
416	حمد خالد حمد البريص المرى	30963407148	14	\N	55377779	2025-11-28 10:38:57.481455
417	راشد مسعود حمد مسعود العذبى	30963400556	14	\N	55853222	2025-11-28 10:38:57.481892
418	سلمان عبدالرحمن	30858600317	14	\N	77474773	2025-11-28 10:38:57.482313
419	شهاب مهدى عمر محمد	30708000016	14	\N	66909626	2025-11-28 10:38:57.482727
420	طالب سعد طالب سعد شفيع	30963404617	14	\N	30296666	2025-11-28 10:38:57.483139
421	طه البصرى ابراهيم رحمة الله	30873601066	14	\N	66957442	2025-11-28 10:38:57.483537
422	عامر محمدأنس عبدالرحمن شيخ النجارين	30976000040	14	\N	33366455	2025-11-28 10:38:57.48395
423	عبدالرحمن عمار شرف زيد	30988600497	14	\N	50403942	2025-11-28 10:38:57.484318
424	عبدالعزير ديق عبدى حسين	30823000007	14	\N	66938554	2025-11-28 10:38:57.484662
425	عبدالله محمود البحرى	30999900215	14	\N	51144700	2025-11-28 10:38:57.485004
426	على شفيع راشد سعيد الفهيده	30963405152	14	\N	55214040	2025-11-28 10:38:57.485346
427	على ظافر فرج ال راشد القحطانى	30963402864	14	\N	31449910	2025-11-28 10:38:57.485677
428	علي حسن ابراهيم محمود ماضى	30999900129	14	\N	66743994	2025-11-28 10:38:57.486012
429	فيصل ناجي حسن محمد القهقوه	31088600058	14	\N	55637805	2025-11-28 10:38:57.486358
430	مجيد عبدالمجيد	30928000083	14	\N	70425828	2025-11-28 10:38:57.486905
431	محمد راشد محمد ابوشهاب المرى	31063402242	14	\N	55202227	2025-11-28 10:38:57.48735
432	محمد زهري غسان  الفاخوري	31076001769	14	\N	70158747	2025-11-28 10:38:57.48781
433	محمد سالم بريك الجربوعى المرى	30963404131	14	\N	55766606	2025-11-28 10:38:57.488429
434	محمد علي احمد العجمي	30951200026	14	\N	55182849	2025-11-28 10:38:57.488838
435	محمد هانى محمد رمضان الصفدى	30999900033	14	\N	55513517	2025-11-28 10:38:57.490155
436	محمد وليد محمد عبدالحليم محمود	30981800620	14	\N	77381981	2025-11-28 10:38:57.490723
437	مروان بلال حسين	30905000047	14	\N	55645134	2025-11-28 10:38:57.491236
438	منذر عمر حامد محمد	30973601161	14	\N	70949044	2025-11-28 10:38:57.491661
439	وليد محمد العبيد بلوله احمد	30973600237	14	\N	66675903	2025-11-28 10:38:57.492327
440	بخيت فهد بخيت على العذبى	30963402117	15	\N	55079997	2025-11-28 10:38:57.49276
441	تميم حمد جارالله الجربوعى المرى	30963403995	15	\N	50194444	2025-11-28 10:38:57.493213
442	تميم حمد سعيد حمد العطان	30963407497	15	\N	55515803	2025-11-28 10:38:57.493606
443	تميم غانم محمد ناصر الدهيمى	30763401723	15	\N	55532106	2025-11-28 10:38:57.494003
444	جارالله سالم بخيت محمد المرى	30978400009	15	\N	50526055	2025-11-28 10:38:57.494357
445	جارالله ناصر حمد البريدى المرى	30963405672	15	\N	55655447	2025-11-28 10:38:57.494714
446	خالد بهاءالدين ابراهيم محمد اهل	30999900036	15	\N	66633063	2025-11-28 10:38:57.495094
447	سعد ناصر سعد شالح الدوسرى	30863406937	15	\N	33288882	2025-11-28 10:38:57.495495
448	صالح سالم صالح بريكان المرى	30963402918	15	\N	77100464	2025-11-28 10:38:57.495861
449	عبدالعزيز ناصر عايد الفريجى الرويلى	31063404691	15	\N	77785858	2025-11-28 10:38:57.49621
450	عبدالله على محمد صالح الكربى	30888600057	15	\N	55290233	2025-11-28 10:38:57.496565
451	عبدالهادى سعيد عبدالهادى البريدى المرى	30963404256	15	\N	66222269	2025-11-28 10:38:57.496929
452	على راشد طالب صالح العذبه	30963403562	15	\N	33355599	2025-11-28 10:38:57.497318
453	على سعيد على الدجران المرى	30963404917	15	\N	0	2025-11-28 10:38:57.497756
454	على سعيد على صالح السفران	30963406056	15	\N	77800144	2025-11-28 10:38:57.498163
455	على سليم على سالم المرى	30963403422	15	\N	66688845	2025-11-28 10:38:57.498587
456	على عبدالله ناصر الهولى النعيمى	30963403084	15	\N	55898948	2025-11-28 10:38:57.498976
457	على محمد صالح ابوصلعه المرى	30863400784	15	\N	55732227	2025-11-28 10:38:57.499354
458	فيصل على عبدالله سهل المرى	30863403664	15	\N	55569090	2025-11-28 10:38:57.499768
459	ماجد منيف ردعان المظفرى الهاجرى	30963400039	15	\N	55568393	2025-11-28 10:38:57.500162
460	مبارك محمد مبارك محمد السوداء	30963402893	15	\N	66703752	2025-11-28 10:38:57.500521
461	مبخوت على مبخوت سالم المرى	30963404499	15	\N	66501020	2025-11-28 10:38:57.500908
462	محمد ابراهيم ربا دريا بورقشمي	30936400131	15	\N	55211471	2025-11-28 10:38:57.501289
463	محمد راشد حمد محمد جرحب	30963406514	15	\N	55315311	2025-11-28 10:38:57.501676
464	محمد راشد عبدالله سهل المرى	30963405317	15	\N	55564060	2025-11-28 10:38:57.502079
465	محمد سالم محمد شبيب الدوسرى	31063406358	15	\N	55000264	2025-11-28 10:38:57.502446
466	محمد سيال بايين رنجين خان	30858600743	15	\N	55792189	2025-11-28 10:38:57.502802
467	محمد طارق ربيع محمد عبدالجواد	30881805374	15	\N	33242134	2025-11-28 10:38:57.503163
468	محمد على راشد الحمد المناعى	30963406010	15	\N	50578928	2025-11-28 10:38:57.503515
469	محمد على سعد السلمان القحطاني	30963402976	15	\N	66087576	2025-11-28 10:38:57.50388
470	موسى صالح موسى على المشعرى	30963406771	15	\N	55479702	2025-11-28 10:38:57.504319
471	هادى محمد هديب الجربوعى المرى	30863405327	15	\N	55557325	2025-11-28 10:38:57.504792
472	الوليد فهيد محمد الزبدان المرى	30863405905	16	\N	66209870	2025-11-28 10:38:57.505263
473	بدر عبدالعزيز حمد حمد العبيدى	30963405282	16	\N	55435054	2025-11-28 10:38:57.506108
474	جابر حمد سعيد الشرقى المرى	30663405842	16	\N	55738965	2025-11-28 10:38:57.506951
475	جابر طالب محمد كليفيخ المنخس	31063401481	16	\N	55564611	2025-11-28 10:38:57.50733
476	حمد على سعيد عفير المرى	30963402922	16	\N	55551575	2025-11-28 10:38:57.507693
477	حمد محمد حمد البحيح المري	30568200183	16	\N	55779795	2025-11-28 10:38:57.508057
478	حمد محمد هادي القحطاني	30968200178	16	\N	70705527	2025-11-28 10:38:57.508407
479	خليفه شاه محمد زيداك بادشاه	30858600146	16	\N	55380892	2025-11-28 10:38:57.50875
480	راشد بخيت راشد المنخس المرى	30963406703	16	\N	55558396	2025-11-28 10:38:57.509101
481	راشد جابر على ال صفور المرى	30963404760	16	\N	66653161	2025-11-28 10:38:57.509459
482	سعد فلاح حسين شايع الحبابى	30963405839	16	\N	55554388	2025-11-28 10:38:57.509848
483	سعيد صالح سعيد حمد ملهيه	30863406834	16	\N	66260377	2025-11-28 10:38:57.510228
484	سعيد طالب عبدالله طالب المنخس	30963402094	16	\N	30458888	2025-11-28 10:38:57.510573
485	سعيد على سعيد سالم مسعود	31163401587	16	\N	33333835	2025-11-28 10:38:57.512014
486	سيف الدين الطنطاوي زكريا الطنطاوى فرج	30981803649	16	\N	77134136	2025-11-28 10:38:57.51431
487	صالح فلاح بريك الغضيض المري	30868200019	16	\N	66878217	2025-11-28 10:38:57.514882
488	طالب عبدالهادى طالب عبدالهادى المرى	31063400215	16	\N	55511881	2025-11-28 10:38:57.515306
489	عبدالقادر احمد محمد حاجي حسين	30870600033	16	\N	55210815	2025-11-28 10:38:57.515705
490	عبدالله جابر هادى على البريدى	31063401715	16	\N	77707222	2025-11-28 10:38:57.516287
491	عبدالله حمد محمد عبدالله دحروج	30963406863	16	\N	66612555	2025-11-28 10:38:57.516667
492	عبدالله سعيد على سعيد ابوشارب	30963403962	16	\N	55528882	2025-11-28 10:38:57.517041
493	عرفان نور حسين حسين خان	30758600799	16	\N	70464644	2025-11-28 10:38:57.517391
494	عمر على ناصر الرواحي	30951200288	16	\N	66845321	2025-11-28 10:38:57.517758
495	عوض هادى عوض السعدى اليافعى	30963407538	16	\N	66312383	2025-11-28 10:38:57.518142
496	متعب راشد متعب المنخس المرى	30963405452	16	\N	70706000	2025-11-28 10:38:57.518494
497	محمد حمد فهد محمد القوبعى	31063406691	16	\N	30000182	2025-11-28 10:38:57.518866
498	محمد زاده	30858601595	16	\N	55399545	2025-11-28 10:38:57.519218
499	محمد سعيد سالم سعيد الاسود	31063400216	16	\N	33333888	2025-11-28 10:38:57.519566
500	محمد على راشد ال سنيد المرى	30963401489	16	\N	70701234	2025-11-28 10:38:57.519937
501	محمد ناصر سالم الهولى النعيمى	30963407025	16	\N	55884855	2025-11-28 10:38:57.520288
502	منصور على منصور على الحوبان	30963400298	16	\N	50404071	2025-11-28 10:38:57.520642
503	ناصر محمد حمد البريد المرى	30863403100	16	\N	55677792	2025-11-28 10:38:57.521014
504	احمد ناهض يوسف محمد القريناوي	30999900151	17	\N	55299740	2025-11-28 10:38:57.521363
505	اسامه خطاب الدين	30958600482	17	\N	66961667	2025-11-28 10:38:57.521714
506	البراء على عويض الصقور المرى	30963405566	17	\N	55152414	2025-11-28 10:38:57.522066
507	تميم محمد على حمد بن نوره	30763406275	17	\N	51199996	2025-11-28 10:38:57.522405
508	جابر على صالح الربيط السنيد	30963404611	17	\N	55088665	2025-11-28 10:38:57.522754
509	جارالله على محمد البريدى المرى	31163400307	17	\N	77733350	2025-11-28 10:38:57.523103
510	حمد حسن راشد حسن الذوادى	30863403212	17	\N	0	2025-11-28 10:38:57.523443
511	حمد على محمد النابت المرى	30963402764	17	\N	55481876	2025-11-28 10:38:57.523802
512	سالم راشد محسن عبدالله ملهيه	30863401070	17	\N	55255746	2025-11-28 10:38:57.524154
513	سالم مبارك على الحلطان المرى	30963406421	17	\N	66744111	2025-11-28 10:38:57.52452
514	سالم محمد طحنون الجبران المرى	30863402025	17	\N	33135999	2025-11-28 10:38:57.524894
515	سعود على بخيت البريدى المرى	30963400578	17	\N	50002112	2025-11-28 10:38:57.525271
516	سعيد راشد سعيد محمد الزكيبا	30963402311	17	\N	74430008	2025-11-28 10:38:57.525658
517	سيف على مسفر سفران المرى	31063400162	17	\N	55543332	2025-11-28 10:38:57.526076
518	طالب حمد محمد جابر عفيفه	30763405696	17	\N	55151231	2025-11-28 10:38:57.526611
519	عبدالرحمن على سالم راشد العذبى	30963403466	17	\N	50175698	2025-11-28 10:38:57.527031
520	عبدالكريم عبدالله عبدالرحمن علي المرباطي	30904800026	17	\N	55909396	2025-11-28 10:38:57.527446
521	عبدالله محمد على حمد بن نوره	30563404367	17	\N	51199996	2025-11-28 10:38:57.527843
522	عبدالله مسفر عبدالله ال سفران المرى	31063405458	17	\N	55551095	2025-11-28 10:38:57.528216
523	على حمد على عبدالله بن نوره	30963400726	17	\N	55009034	2025-11-28 10:38:57.528565
524	على رشيد على الخطلاء السنيد	30963400288	17	\N	66568948	2025-11-28 10:38:57.528903
525	فالح فهد صبيح الفريجى الرويلى	30963406547	17	\N	55877565	2025-11-28 10:38:57.529251
526	فرج محمد حمد صالح الشرقى	30863405565	17	\N	66715177	2025-11-28 10:38:57.529611
527	فهد على محمد راشد المرى	30963405972	17	\N	55319964	2025-11-28 10:38:57.530247
528	محمد جارالله محمد ال بريد المرى	30963401701	17	\N	55774033	2025-11-28 10:38:57.530824
529	محمد راشد محمد حمد شاجع	30663407052	17	\N	70598888	2025-11-28 10:38:57.531204
530	محمد عبدالله حمد سعيد ابوشارب	30963403257	17	\N	66599939	2025-11-28 10:38:57.531714
531	محمد عبدالله محمد حمد دحروج	30963405661	17	\N	55590355	2025-11-28 10:38:57.532345
532	محمد على محمد راشد المرى	30663401240	17	\N	55319964	2025-11-28 10:38:57.532845
533	محمد فلاح بريك الغضيض المري	30968200050	17	\N	66878217	2025-11-28 10:38:57.533318
534	محمد وعل عوض ال العبد القحطاني	30668200330	17	\N	51289996	2025-11-28 10:38:57.533803
535	تميم جارالله محمد ذفال الحبابي	30763400757	18	\N	33369317	2025-11-28 10:38:57.534269
536	تميم هادى محمد راشد المرى	30941400028	18	\N	33407954	2025-11-28 10:38:57.534663
537	جابر على محمد المسلط العتيبى	30763402860	18	\N	55042220	2025-11-28 10:38:57.53506
538	حسين جابر حسين العاض المرى	30963402758	18	\N	70704447	2025-11-28 10:38:57.535427
539	حمد مسعود راشد حمد العذبي	30963405303	18	\N	55302121	2025-11-28 10:38:57.535883
540	راشد جابر صالح ال سنيد المرى	30963403642	18	\N	66333625	2025-11-28 10:38:57.536245
541	راشد سالم حمد التويجر المرى	30863401352	18	\N	55003997	2025-11-28 10:38:57.536597
542	راشد طالب محمد المري	30768200065	18	\N	66187204	2025-11-28 10:38:57.536955
543	راشد محمد حمد البحيح المري	30668200162	18	\N	55779795	2025-11-28 10:38:57.537318
544	سالم على مبارك بن نوره المرى	30963402645	18	\N	55557535	2025-11-28 10:38:57.537684
545	سالم محمد سالم سعيد بن نوره	30863400609	18	\N	55484445	2025-11-28 10:38:57.538069
546	سعود محمد عبدالله ال نابت المرى	30963400368	18	\N	55155444	2025-11-28 10:38:57.53867
547	سلطان ماجد سعد شالح الدوسرى	30963407542	18	\N	55556341	2025-11-28 10:38:57.539069
548	صالح سعد صالح محمد النابت	30863402435	18	\N	55005118	2025-11-28 10:38:57.539431
549	صياح راشد سعيد صياح المنصورى	30963404305	18	\N	55522518	2025-11-28 10:38:57.539793
550	عبدالعزيز فهد سعود على الحنزاب	30963406938	18	\N	55000485	2025-11-28 10:38:57.540156
551	عبدالله جابر صالح ال مسعود المرى	30963404861	18	\N	55733385	2025-11-28 10:38:57.540526
552	عبدالله طالب حمد صالح العذبه	30963405855	18	\N	55070056	2025-11-28 10:38:57.540907
553	عبدالله على محمد سعيد عزب	30963401618	18	\N	30292222	2025-11-28 10:38:57.5413
554	عبدالله فاروق محمد	30958601247	18	\N	55408036	2025-11-28 10:38:57.54169
555	عبدالله محمد راشد محمد ظرفان	30963404851	18	\N	55622235	2025-11-28 10:38:57.542114
556	على سعد على الهولى النعيمى	30963404504	18	\N	74400440	2025-11-28 10:38:57.542562
557	على ناصر سليم ناصر المرى	30963405172	18	\N	55555645	2025-11-28 10:38:57.543046
558	متعب بخيت متعب المنخس المرى	30963400225	18	\N	50001020	2025-11-28 10:38:57.543438
559	محمد حمد محمد على الجرحب	30963402688	18	\N	55877274	2025-11-28 10:38:57.543812
560	محمد سالم سعيد البحيح المرى	30963405665	18	\N	55508049	2025-11-28 10:38:57.544148
561	محمد على العذاب	30876001028	18	\N	30388577	2025-11-28 10:38:57.54447
562	محمد على سعيد العوامى المرى	30963400494	18	\N	55544166	2025-11-28 10:38:57.544793
563	محمد فهد سعيد الحول المرى	30963401600	18	\N	55555228	2025-11-28 10:38:57.545106
564	هزاع عبدالمنعم	30958601840	18	\N	77912292	2025-11-28 10:38:57.545413
565	بندر سعود حمد ال جبران القحطانى	30963403818	19	\N	77605650	2025-11-28 10:38:57.545712
566	تميم محمد على حامد الجابرى	30963401554	19	\N	77912292	2025-11-28 10:38:57.546768
567	راشد على راشد سعيد الغرينيق	30963403496	19	\N	50261555	2025-11-28 10:38:57.547207
568	راشد محمد راشد حمد عضيبه	30763405092	19	\N	55996060	2025-11-28 10:38:57.547566
569	سعيد حمد بطى محمد الحول	30963405300	19	\N	66888871	2025-11-28 10:38:57.547916
570	سلطان راشد محمد الحسناء المرى	31063401703	19	\N	55866366	2025-11-28 10:38:57.548247
571	سلمان على راشد عليان المرى	30963402146	19	\N	55593790	2025-11-28 10:38:57.548571
572	عامر علي عمر الجعيدى	30888600391	19	\N	55221098	2025-11-28 10:38:57.548907
573	عبدالرحمن على حمد سعيد القاشوطى	30963406363	19	\N	55766266	2025-11-28 10:38:57.549224
574	عبدالرحمن ناصر محمد الزبدان المرى	30963405575	19	\N	33978188	2025-11-28 10:38:57.549536
575	عبدالعزيز جارالله محمد ذفال الحبابي	30963402873	19	\N	70237991	2025-11-28 10:38:57.549858
576	عبدالعزيز سعيد على راشد عضيبه	30963406303	19	\N	55155650	2025-11-28 10:38:57.550208
577	عبدالله سعيد محمد ال نوره المرى	30963406393	19	\N	55055744	2025-11-28 10:38:57.550506
578	عبدالله على محمد جابر عفيفه	30963406359	19	\N	55144417	2025-11-28 10:38:57.550844
579	عبدالله ناصر سعيد المريزيق المرى	30763402151	19	\N	55300313	2025-11-28 10:38:57.551173
580	على بخيت سالم محمد المرى	30963402772	19	\N	77780003	2025-11-28 10:38:57.551476
581	على جابر محمد البريدى المرى	30963400930	19	\N	55989813	2025-11-28 10:38:57.551805
582	غانم جارالله غانم العذبه المرى	30963404363	19	\N	66526444	2025-11-28 10:38:57.552124
583	غانم محسن محمد قائد الرياشي	30988600190	19	\N	55913136	2025-11-28 10:38:57.552438
584	فرج على فرج ال سليم المرى	30963405407	19	\N	33332901	2025-11-28 10:38:57.552795
585	محمد حمد سعيد سالم هطيل	30963406288	19	\N	55848248	2025-11-28 10:38:57.553158
586	محمد حمد محمد عبدالله دحروج	30863400546	19	\N	66612555	2025-11-28 10:38:57.553722
587	محمد سيد بابكر حسن	30873601103	19	\N	0	2025-11-28 10:38:57.554316
588	محمد فهيد على الغفران المرى	30963401290	19	\N	55190823	2025-11-28 10:38:57.554984
589	محمد فيصل حمد الجربوعى المرى	30863405586	19	\N	55501055	2025-11-28 10:38:57.555411
590	محمد مسعود هادى ال درع الحبابى	30963404938	19	\N	55201511	2025-11-28 10:38:57.556954
591	مشعل فرحان سعد ال غراب القحطانى	30963404902	19	\N	55511260	2025-11-28 10:38:57.557569
592	ناصر هادى محمد الزبدان المرى	30963405253	19	\N	50124115	2025-11-28 10:38:57.557986
593	نايف مقبل عبده احمد الحمرى	30988600050	19	\N	0	2025-11-28 10:38:57.558385
594	هاشم على غانم العذبه المرى	30963406694	19	\N	55870667	2025-11-28 10:38:57.558759
595	جابر سالم على الجربوعى المرى	30563404327	20	\N	66569276	2025-11-28 10:38:57.559104
596	جاسم ناصر جارالله العذبه المري	30968200364	20	\N	71111727	2025-11-28 10:38:57.559434
597	جلوي مبارك جلوي الدوسري	30968200067	20	\N	33363050	2025-11-28 10:38:57.559923
598	حمد سالم صالح بريكان المرى	30863403146	20	\N	77100464	2025-11-28 10:38:57.560332
599	حمد على حمد زايد الفهيدى	30663404502	20	\N	66590503	2025-11-28 10:38:57.560679
600	حمد علي حمد بن نوره المري	30878400047	20	\N	33096362	2025-11-28 10:38:57.561018
601	حمد محمد حمد ال معيان المرى	30963405589	20	\N	50005375	2025-11-28 10:38:57.56134
602	حمد محمد حمد الانقح المرى	30863405263	20	\N	55887459	2025-11-28 10:38:57.561667
603	خالد صالح محمد السندوانه المرى	31063403993	20	\N	55677137	2025-11-28 10:38:57.562016
604	خالد مبارك حمد ال جهويل المرى	30963403110	20	\N	55521009	2025-11-28 10:38:57.562331
605	راشد حمد راشد حمد صبيح	30963401697	20	\N	55598566	2025-11-28 10:38:57.562747
606	سالم حمد سالم محمد المرى	30963400655	20	\N	55302223	2025-11-28 10:38:57.563099
607	سالم صالح محمد سعيد المرى	30878400010	20	\N	33093909	2025-11-28 10:38:57.563629
608	سالم على حمد سالم عفيفه	30863405848	20	\N	55705805	2025-11-28 10:38:57.564074
609	سالم على سالم اليربوعى المرى	30963405673	20	\N	55070050	2025-11-28 10:38:57.564421
610	سعود فهد عبدالله محمد العامرى	31063403698	20	\N	55254697	2025-11-28 10:38:57.564761
611	على جبران جازع ال مالك القحطانى	30963401280	20	\N	77772218	2025-11-28 10:38:57.565091
612	على حسين على صالح السفران	30863402766	20	\N	33080003	2025-11-28 10:38:57.565395
613	على حمد سعيد حديد المرى	30863402196	20	\N	77442220	2025-11-28 10:38:57.565701
614	على عبدالله صالح السندوانه المرى	30963401001	20	\N	55100543	2025-11-28 10:38:57.566033
615	على فهد على صالح العذبه	30863406188	20	\N	55693337	2025-11-28 10:38:57.566341
616	على محسن محمد فطيس المرى	30963401564	20	\N	55555401	2025-11-28 10:38:57.566641
617	على مسعود على صالح العذبه	30963402984	20	\N	55429993	2025-11-28 10:38:57.566974
618	مبارك شافى مبارك الساعى الهاجرى	30963407493	20	\N	31114440	2025-11-28 10:38:57.567284
619	مبخوت محمد سالم اليربوعى المرى	30863406329	20	\N	55821666	2025-11-28 10:38:57.567592
620	محمد حمد راشد محسن عبدان	30963406287	20	\N	55401666	2025-11-28 10:38:57.567913
621	محمد فهد منصور منيخر منيخر	30963404014	20	\N	55038387	2025-11-28 10:38:57.568223
622	محمد ناصر بخيت العذبه المرى	30963405776	20	\N	55808160	2025-11-28 10:38:57.568532
623	ناصر سالم محمد حمد العيده	30963406259	20	\N	33338300	2025-11-28 10:38:57.568851
624	ناصر محمد ناصر المريزيق المرى	30963406513	20	\N	33354445	2025-11-28 10:38:57.569166
625	نمر راشد حمد العوير المريزيق	30963401024	20	\N	33995626	2025-11-28 10:38:57.569474
626	ابراهيم محمود ابراهيم حسين عثمان	30981800258	21	\N	66404649	2025-11-28 10:38:57.569795
627	احمد عمر على محمد احمد	30773600668	21	\N	55904001	2025-11-28 10:38:57.570116
628	احمد موسى علي القرارعه	30840001531	21	\N	50434121	2025-11-28 10:38:57.57042
629	أحمد حميد احمد السلامه	30876000144	21	\N	66985637	2025-11-28 10:38:57.570729
630	حسام مصطفى امين مصطفى دلول	30799900256	21	\N	55858106	2025-11-28 10:38:57.571051
631	حمد جول ارشد	30758601151	21	\N	70044497	2025-11-28 10:38:57.571357
632	حمد محمد حمد الزيوح مسعود	31063400745	21	\N	55557591	2025-11-28 10:38:57.571661
633	خالد محسن حسين على حسين	30888600517	21	\N	77881170	2025-11-28 10:38:57.57198
634	راشد خالد ناصر راشد المقارح	30963402337	21	\N	66665488	2025-11-28 10:38:57.572283
635	رعد على عبدالله صالح العجى	30888600332	21	\N	55317311	2025-11-28 10:38:57.57259
636	سامي عمر نشبت	30884000083	21	\N	55285176	2025-11-28 10:38:57.572906
637	سعيد حمد عبدالله مبارك بن نوره	30963400743	21	\N	55551171	2025-11-28 10:38:57.573213
638	شامخ راشد محمد الحسناء المرى	30963400867	21	\N	55866366	2025-11-28 10:38:57.573546
639	عبدالرحمن سعد سالم الهولى النعيمى	30863406621	21	\N	55009229	2025-11-28 10:38:57.573873
640	عبدالرحمن فاروق محمد	30858601184	21	\N	55408036	2025-11-28 10:38:57.574189
641	عبدالله خالد بليهين حزام القحطانى	30863405334	21	\N	50803030	2025-11-28 10:38:57.5745
642	عبدالله على سعيد محمد الاسود	30863401369	21	\N	55972284	2025-11-28 10:38:57.574821
643	عبدالمنعم جميل العلي	30876001310	21	\N	50391510	2025-11-28 10:38:57.575126
644	على مبارك سعيد حمد جميله	30863401903	21	\N	55200667	2025-11-28 10:38:57.575431
645	غسان ابن عمر التجانى الشيخ	30773600428	21	\N	33860317	2025-11-28 10:38:57.575757
646	فارس طارق جهاد يوسف ابوناهيه	30999900025	21	\N	55854956	2025-11-28 10:38:57.576467
647	فهد سعيد فهد الخديعه المرى	30863405669	21	\N	77577676	2025-11-28 10:38:57.577432
648	مبارك جمعان حسيان ال رشيد الهاجرى	30863404930	21	\N	55845252	2025-11-28 10:38:57.578553
649	مبارك سعيد مبارك سعيد الجهويل	30863400325	21	\N	33008113	2025-11-28 10:38:57.580004
650	محمد احمدالله	30735601767	21	\N	55422123	2025-11-28 10:38:57.580728
651	محمد عبدالهادى محمد الحيمر المرى	30841400034	21	\N	33653555	2025-11-28 10:38:57.581227
652	محمد ياسر طاهر محمد	30788600585	21	\N	55462928	2025-11-28 10:38:57.58165
653	معتصم مصطفى محمد علي معوض	30881804654	21	\N	66310836	2025-11-28 10:38:57.582035
654	ناصر صالح صالح حسين القحطاني	30863403260	21	\N	55892801	2025-11-28 10:38:57.582391
655	نايف احمد سعيد المدول	30888600689	21	\N	55098222	2025-11-28 10:38:57.582757
656	هاشم عبدالله هاشم عبدالدائم على	30873600185	21	\N	55740176	2025-11-28 10:38:57.583101
657	يوسف سيد ربيع عبدالفتاح جنيدي	30881802550	21	\N	33121446	2025-11-28 10:38:57.583437
658	جابر بخيت عبدالله البريدى المرى	30963403929	22	\N	55035031	2025-11-28 10:38:57.583799
659	جابر عبدالله محمد ال نشيره المرى	30963402776	22	\N	55210153	2025-11-28 10:38:57.584133
660	حمد محمد حمد محمد عضيبه	30863407158	22	\N	55801717	2025-11-28 10:38:57.584465
661	خالد حمد على راشد المري	30878400013	22	\N	55505735	2025-11-28 10:38:57.584798
662	راشد غانم مبارك الساعى الهاجرى	30763405292	22	\N	70704442	2025-11-28 10:38:57.585121
663	زابن راشد زابن ال زابن الدوسرى	30863407225	22	\N	55552870	2025-11-28 10:38:57.585436
664	سالم عبدالله سالم اليربوعى المرى	30863403309	22	\N	77779320	2025-11-28 10:38:57.585757
665	سالم عبدالله سالم محمد المرى	30863404477	22	\N	55947878	2025-11-28 10:38:57.586078
666	سعيد سيف سعيد السنارى الجحيش	30563403274	22	\N	55221981	2025-11-28 10:38:57.586394
667	سعيد مبارك سعيد صياح المنصورى	30763403407	22	\N	66180085	2025-11-28 10:38:57.586704
668	سفر محمد مبارك الساعى الهاجرى	30863404068	22	\N	55571188	2025-11-28 10:38:57.58706
669	سلطان مبارك حسن مقرى الكربى	30863405533	22	\N	55550344	2025-11-28 10:38:57.587375
670	سهيل سالم محمد كده	30851200219	22	\N	66444179	2025-11-28 10:38:57.587685
671	شافى ماجد شافى ماجد المنصورى	30863404670	22	\N	55070220	2025-11-28 10:38:57.588016
672	عبدالرحمن صالح محمد سالم النابت	30763404706	22	\N	55900639	2025-11-28 10:38:57.588397
673	عبدالهادى محمد عبدالهادى حبيشه النابت	30963403079	22	\N	55823491	2025-11-28 10:38:57.588715
674	عسكر محمد حسن محمد الكربى	30863401487	22	\N	77190158	2025-11-28 10:38:57.589238
675	على سعيد سيف السنارى الجحيش	30663403705	22	\N	77143387	2025-11-28 10:38:57.589555
676	عويد حمود عويد قريان الهاجرى	30763403534	22	\N	77555844	2025-11-28 10:38:57.589873
677	فلاح على فلاح على محميد	30763400920	22	\N	55022294	2025-11-28 10:38:57.590187
678	فهد سالم على حوبان الحوبان	30863403425	22	\N	55551369	2025-11-28 10:38:57.590496
679	فهد طالب عبدالله طالب المنخس	30663405067	22	\N	55555748	2025-11-28 10:38:57.590857
680	مبارك هادى على الحلطان المرى	30563405520	22	\N	55568086	2025-11-28 10:38:57.591188
681	محمد جابر حمد النابت المرى	30863400227	22	\N	55222608	2025-11-28 10:38:57.591509
682	محمد جابر راشد جابر السنارى	30663406579	22	\N	66058666	2025-11-28 10:38:57.591842
683	محمد على حمد سعيد القاشوطى	30863400514	22	\N	55766266	2025-11-28 10:38:57.592162
684	محمد مشعل محمد راشد المنخس	30863402327	22	\N	55324670	2025-11-28 10:38:57.592483
685	مذكر حمود عويد قريان الهاجرى	30863405001	22	\N	77555844	2025-11-28 10:38:57.592818
686	ناصر عايض ناصر ال فطيح القحطاني	30868200044	22	\N	66617333	2025-11-28 10:38:57.593148
687	ناصر محمد ناصر البحيح المرى	30663402720	22	\N	55022217	2025-11-28 10:38:57.593463
688	احمد ابراهيم عبدالقادر طاهر الخزرجى	30888600027	23	\N	55594439	2025-11-28 10:38:57.593786
689	احمد امجد علي عثمان	30873601094	23	\N	55594439	2025-11-28 10:38:57.594125
690	احمد عوض احمد العوض	30873601481	23	\N	55206674	2025-11-28 10:38:57.594439
691	احمد ماهر احمد مبارك احمد	30881801926	23	\N	66581371	2025-11-28 10:38:57.594771
692	انس محمد امين احمد الزراف	30888600178	23	\N	66004611	2025-11-28 10:38:57.595092
693	جهاد منصور حاجى نعيمى	30936400253	23	\N	66887335	2025-11-28 10:38:57.595569
694	حمد عبدالعزيز على البحيح المرى	30663405630	23	\N	55802099	2025-11-28 10:38:57.595922
695	خالد محمد ابراهيم الشديفات	30940000916	23	\N	66867575	2025-11-28 10:38:57.596261
696	خالد وليد البدر محمد مشوق	30888600079	23	\N	55426770	2025-11-28 10:38:57.596605
697	سعود حسن هلال حسن العماش	30863405717	23	\N	55807434	2025-11-28 10:38:57.596978
698	سعيد ناصر سعيد الغنبوصي	30851200187	23	\N	55182906	2025-11-28 10:38:57.597317
699	شاهد شميم	30835601427	23	\N	55304970	2025-11-28 10:38:57.598189
700	عبدالرحمن حمد سعيد الخفير القرني	30963401807	23	\N	77040550	2025-11-28 10:38:57.598654
701	عبدالرحمن عبدالظاهر خان	30758600452	23	\N	55139396	2025-11-28 10:38:57.599044
702	عبدالله احمد يوسف جاسم اليعقوب	30663406336	23	\N	55699976	2025-11-28 10:38:57.599408
703	على سالم راشد المرى	30868200006	23	\N	50080222	2025-11-28 10:38:57.599859
704	على سعيد صالح الصوفى	30788600487	23	\N	55432342	2025-11-28 10:38:57.600247
705	عمار محمد محمد ابوزيد حسن	31081805523	23	\N	30244665	2025-11-28 10:38:57.600604
706	عمر عبدالرحمن على محمد	30858600242	23	\N	55350936	2025-11-28 10:38:57.600958
707	عمرو محمد ملاحي محمود طافش	30881803431	23	\N	66950655	2025-11-28 10:38:57.601293
708	فيصل سلطان فيصل المسافره الهاجرى	30963407524	23	\N	55049831	2025-11-28 10:38:57.601631
709	محمد امين سعيد عوض باصبيح	30888600300	23	\N	55184981	2025-11-28 10:38:57.601971
710	محمد منتصر ابراهيم عيسى محمد	30773600041	23	\N	55661436	2025-11-28 10:38:57.602306
711	محمدعمر ناظم بيك	30776200002	23	\N	55963727	2025-11-28 10:38:57.602639
712	ناصر مسعود ناصر المري	31068200155	23	\N	66616021	2025-11-28 10:38:57.602975
713	يوسف وليد محمد عبدالحليم محمود	30781801577	23	\N	55560240	2025-11-28 10:38:57.603286
714	الوليد خالد وليد فضل حجى	30899900151	24	\N	55740721	2025-11-28 10:38:57.603624
715	تميم على نجود بخيت الكثيرى	30763405771	24	\N	55840744	2025-11-28 10:38:57.603958
716	جابر هادى حمد الزبدان المرى	30863405138	24	\N	66647111	2025-11-28 10:38:57.604277
717	حمد على محمد على المرى	30763402373	24	\N	55155981	2025-11-28 10:38:57.604593
718	خالد على محمد راشد المرى	30763406048	24	\N	55400551	2025-11-28 10:38:57.604913
719	خالد محمد ناصر البريد المرى	30863400096	24	\N	55232739	2025-11-28 10:38:57.605231
720	راشد حمد راشد المنخس المرى	30763401155	24	\N	55558396	2025-11-28 10:38:57.605539
721	سالم حمد عبدالهادى حذقين المرى	30863405176	24	\N	31112228	2025-11-28 10:38:57.608092
722	سالم مسفر سالم سعيد الحديد	30863401564	24	\N	0	2025-11-28 10:38:57.608771
723	سعيد محسن سعيد كده المهري	30768200034	24	\N	55747945	2025-11-28 10:38:57.610245
724	صالح سعيد صالح محمد ابوصلعه	30563402926	24	\N	0	2025-11-28 10:38:57.610681
725	صمغه سعيد محسن حمد ابوصلعه	30863401748	24	\N	55634885	2025-11-28 10:38:57.611091
726	طالب هادى على الحلطان المرى	30863406199	24	\N	55568086	2025-11-28 10:38:57.611462
727	عبدالعزيز حصين على محمد حذقين	30763402178	24	\N	31119443	2025-11-28 10:38:57.61185
728	عبدالله سعيد حمد العذبه المرى	30663405587	24	\N	33555323	2025-11-28 10:38:57.612212
729	عبدالله سيف على عبدالله سفران	30863400768	24	\N	55122366	2025-11-28 10:38:57.612558
730	على عامر على الغفرانى المرى	30763402188	24	\N	55554882	2025-11-28 10:38:57.612907
731	على عبدالله هادى البريد المرى	30663402775	24	\N	55109911	2025-11-28 10:38:57.613307
732	عمر سعيد علي المري	30568200293	24	\N	50063022	2025-11-28 10:38:57.61585
733	فرج محمد سالم البريص المرى	30763400004	24	\N	55845885	2025-11-28 10:38:57.616542
734	فهد ناصر عايد الفريجى الرويلى	30963402978	24	\N	77785858	2025-11-28 10:38:57.617016
735	فيصل سعود فيصل حنزاب المرى	30863406790	24	\N	55822249	2025-11-28 10:38:57.617434
736	فيصل سعود محمد سعود نقادان	30463400398	24	\N	55835802	2025-11-28 10:38:57.618175
737	فيصل سعود محمد فهد العذبه	30463404954	24	\N	55321207	2025-11-28 10:38:57.619851
738	محمد راشد محمد راشد القرنيق	30663406109	24	\N	55487777	2025-11-28 10:38:57.620287
739	مسعود احمد وادى مسرهد الشمرى	30863407139	24	\N	55020044	2025-11-28 10:38:57.620848
740	منصور عبدالهادى حمد هادى حذقين	30863403927	24	\N	55559022	2025-11-28 10:38:57.621262
741	منصور فهد منصور منيخر منيخر	30863401688	24	\N	55038387	2025-11-28 10:38:57.621653
742	ناصر راشد محمد النابت المرى	30563405437	24	\N	55544979	2025-11-28 10:38:57.622033
743	وافى على سعيد محمد ملهيه	30763402574	24	\N	55885857	2025-11-28 10:38:57.622408
744	احمد جمل عويلى المقاطى العتيبى	30863405746	25	\N	66993282	2025-11-28 10:38:57.62279
745	جابر ناصر حصين ناصر المرى	30863403472	25	\N	55569500	2025-11-28 10:38:57.623169
746	جارالله على محمد جابر عفيفه	30863405536	25	\N	55144417	2025-11-28 10:38:57.623533
747	حمد راشد حمد محمد جرحب	30863404343	25	\N	55315311	2025-11-28 10:38:57.623898
748	راشد سالم راشد الجرابعه المرى	30463403386	25	\N	55777891	2025-11-28 10:38:57.624248
749	راشد سعيد راشد سعيد الغرينيق	30763405032	25	\N	55055539	2025-11-28 10:38:57.624597
750	راشد على مبارك الهامله المرى	30763405445	25	\N	55571266	2025-11-28 10:38:57.624957
751	سالم حسين على محمد الجرحب	30863407082	25	\N	55656444	2025-11-28 10:38:57.625315
752	سالم سعيد مبارك النابت المرى	30863400527	25	\N	55553431	2025-11-28 10:38:57.625652
753	سالم محمد بخيت سالم الابهق	30763405572	25	\N	55999399	2025-11-28 10:38:57.625997
754	سالم محمد سالم سعيد الاسود	30863401985	25	\N	55112777	2025-11-28 10:38:57.626358
755	سامر عبدالرحمن شاهر حمود	30640000206	25	\N	55865631	2025-11-28 10:38:57.626716
756	سعد عبدالله سعد البويصم المرى	30863400319	25	\N	50841110	2025-11-28 10:38:57.627073
757	سعيد على سيف ال سفران المرى	30863405740	25	\N	55305083	2025-11-28 10:38:57.627452
758	سعيد مسفر صالح سعيد السفران	30663405468	25	\N	55231617	2025-11-28 10:38:57.627846
759	سلطان راشد حمد ال مسعود المرى	30863405591	25	\N	31322002	2025-11-28 10:38:57.628188
760	صالح محسن سالم الجربوعى المرى	30263402230	25	\N	66556068	2025-11-28 10:38:57.628537
761	عايض حسن عايض ال مسفر القحطاني	30568200241	25	\N	50132086	2025-11-28 10:38:57.628964
762	عبدالله جارالله على الجربوعى المرى	30863400572	25	\N	66542220	2025-11-28 10:38:57.629344
763	عبدالله سعيد عبدالله محمد السنارى	30863400690	25	\N	33796903	2025-11-28 10:38:57.629706
764	عبدالله محمد عبدالله سعيد بوصلعه	30763402829	25	\N	66666632	2025-11-28 10:38:57.630127
765	على سعيد على الجرحب المرى	30863400204	25	\N	55433320	2025-11-28 10:38:57.630516
766	على عبدالله على عوض المقدم	30663404673	25	\N	33335370	2025-11-28 10:38:57.630985
767	عويمر سالم عويمر غاشم الكثيرى	30663402354	25	\N	66727605	2025-11-28 10:38:57.631371
768	فهد محمد على محمد بالحارث	30863400944	25	\N	66557781	2025-11-28 10:38:57.631713
769	محمد حمد سالم محمد المرى	30863406366	25	\N	55305004	2025-11-28 10:38:57.632073
770	محمد راشد محمد حمد دجران	30663404417	25	\N	33055606	2025-11-28 10:38:57.632395
771	محمد عبدالرحمن محمد جادالله عارف	30881801434	25	\N	55613006	2025-11-28 10:38:57.632712
772	محمد ناصر جابر الزبدانى المرى	30863405742	25	\N	55029137	2025-11-28 10:38:57.633072
773	ناصر محمد ناصر مبارك الحنزاب	30863407559	25	\N	33939976	2025-11-28 10:38:57.633397
774	ابراهيم خليل ابراهيم عبدالخالق صالح	30858600324	26	\N	66010102	2025-11-28 10:38:57.633721
775	احمد شاهين محمد ابومجيريعه المنصوري	30878400019	26	\N	33178853	2025-11-28 10:38:57.634256
776	تميم حسن محمد جربوع الكربى	30763404964	26	\N	55560025	2025-11-28 10:38:57.634606
777	جابر على جابر البريدى المرى	30863404936	26	\N	55000438	2025-11-28 10:38:57.63496
778	حامد مذكر جبران ال كزمان القحطانى	30663401687	26	\N	77890184	2025-11-28 10:38:57.635304
779	حمد زيد محمد الحسناء المرى	30763401305	26	\N	77535333	2025-11-28 10:38:57.635634
780	حمد صالح طالب صالح العذبه	30863406257	26	\N	33555999	2025-11-28 10:38:57.637971
781	حمد صالح محمد السندوانه المرى	30863405388	26	\N	66189877	2025-11-28 10:38:57.638472
782	حمد على حمد النابت المرى	30863401347	26	\N	55707779	2025-11-28 10:38:57.638859
783	حمد محمد راشد حمد عضيبه	30863406949	26	\N	55625551	2025-11-28 10:38:57.639234
784	خالد محمد على محمد الجرحب	30863405051	26	\N	55485151	2025-11-28 10:38:57.639584
785	راشد صالح حمد محمد عضيبه	30963407197	26	\N	77773500	2025-11-28 10:38:57.639942
786	زيد محمد حزام انديله المرى	30863403841	26	\N	55884844	2025-11-28 10:38:57.640292
787	سالم سعيد ناصر محمد النابت	30863402689	26	\N	55303092	2025-11-28 10:38:57.640635
788	سالم مبارك محمد النابت المرى	30863402831	26	\N	55551430	2025-11-28 10:38:57.641201
789	سعيد عبدالله على حمد البريد	30963406263	26	\N	55522866	2025-11-28 10:38:57.641586
790	طالب بخيت سعيد طالب المنخس	30563400680	26	\N	55599114	2025-11-28 10:38:57.642009
791	عبدالرحمن محمد جابر كردى المنخس	30863404316	26	\N	55033535	2025-11-28 10:38:57.642362
792	عبدالله صلاح زيد سعيد علوى	30888600122	26	\N	55399161	2025-11-28 10:38:57.642717
793	عبدالله منيف ردعان المظفرى الهاجرى	30763402432	26	\N	55568393	2025-11-28 10:38:57.643082
794	على جابر عبدالله محمد السنارى	30863401877	26	\N	74493327	2025-11-28 10:38:57.643428
795	علي مناع مبارك الغييثي الدوسري	30868200205	26	\N	33210021	2025-11-28 10:38:57.650856
796	فارس محمد هادى محمد الفهيده	30863405696	26	\N	55803338	2025-11-28 10:38:57.651453
797	فهد مبخوت راشد جزوى المسعود	30863404892	26	\N	55728271	2025-11-28 10:38:57.651853
798	محمد جاويد نور محمد	30858600337	26	\N	55614942	2025-11-28 10:38:57.652209
799	محمد حسين على جرحب المرى	30863403727	26	\N	55537971	2025-11-28 10:38:57.652567
800	محمد راشد محمد حمد الحول	30763404361	26	\N	33411110	2025-11-28 10:38:57.652949
801	محمد سالم حمد سالم دحبج	30863406528	26	\N	55010403	2025-11-28 10:38:57.653296
802	محمد سعيد ناصر محمد هطيل	30463401713	26	\N	55092023	2025-11-28 10:38:57.653661
803	محمد ناصر حمد البريدى المرى	30863402085	26	\N	55559706	2025-11-28 10:38:57.654022
804	ناصر صالح على السنارى الجحيش	30863404652	26	\N	59926600	2025-11-28 10:38:57.654357
805	نايف مبارك فرج حفيظ المرى	30763406800	26	\N	66662167	2025-11-28 10:38:57.654815
806	احمد عوض احمد عوض الهزاع	30863406416	27	\N	55242555	2025-11-28 10:38:57.655141
807	جابر محمد جابر البريد المرى	30963400147	27	\N	55000284	2025-11-28 10:38:57.655474
808	حسين صالح حسين سعيد السفران	30663403640	27	\N	66730520	2025-11-28 10:38:57.655801
809	حمد سعود حمد محمد سعود	30688600755	27	\N	0	2025-11-28 10:38:57.658834
810	حمد سعيد تويم محمد القاشوطى	30763405574	27	\N	55110208	2025-11-28 10:38:57.659509
811	حمد على محمد البريدى المرى	30963405101	27	\N	55521325	2025-11-28 10:38:57.659903
812	خالد سعيد مستور ال الشريف القحطانى	30863401947	27	\N	55222380	2025-11-28 10:38:57.660271
813	خالد محمد راشد محمد ظرفان	30863404270	27	\N	55440863	2025-11-28 10:38:57.66064
814	راشد عبدالله راشد الزبدانى المرى	30763402921	27	\N	55090699	2025-11-28 10:38:57.661002
815	راشد محمد سالم محمد الاسود	30863400350	27	\N	55653338	2025-11-28 10:38:57.661361
816	سالم صالح عبدالله الاحول الجحيش	30863406095	27	\N	55050847	2025-11-28 10:38:57.661699
817	سالم مبارك سعد النابت المرى	30863402526	27	\N	55557869	2025-11-28 10:38:57.662051
818	سعد حمد ناصر الهولى النعيمى	30763405948	27	\N	55535452	2025-11-28 10:38:57.662403
819	سعيد راشد عبدالله على عفيفه	30663406391	27	\N	66808606	2025-11-28 10:38:57.662729
820	سيف الله غلام رضا زكريا خان	30358600921	27	\N	55340526	2025-11-28 10:38:57.663063
821	صالح على صالح الربيط السنيد	30463401769	27	\N	55088665	2025-11-28 10:38:57.664197
822	صالح على محمد النابت المرى	30763400331	27	\N	55481876	2025-11-28 10:38:57.664577
823	عبدالرحمن محمد على ال برمان القحطانى	30863407607	27	\N	55552761	2025-11-28 10:38:57.664923
824	عبدالعزيز بخيت محمد دغش جميله	30863405982	27	\N	33379026	2025-11-28 10:38:57.66525
825	عبدالله سعيد صالح محمد ابوصلعه	30963405729	27	\N	55600899	2025-11-28 10:38:57.665578
826	عبدالله مبارك شليويح مبارك رملان	30863404743	27	\N	55559287	2025-11-28 10:38:57.665926
827	عبدالله ناصر حمد البريد المرى	30763406440	27	\N	55866133	2025-11-28 10:38:57.666243
828	عزيز محمد حمد محمد العبيدى	30763404367	27	\N	77888117	2025-11-28 10:38:57.666565
829	على جابر طحنون الجبران المرى	30863400394	27	\N	55867876	2025-11-28 10:38:57.66689
830	على سالم على راجح المري	30878400049	27	\N	0	2025-11-28 10:38:57.667204
831	على محمد راشد الخديعه المرى	30663406946	27	\N	50014999	2025-11-28 10:38:57.669834
832	فارس سعيد حمد الجربوعى المرى	30863406953	27	\N	55644078	2025-11-28 10:38:57.670393
833	فهد على حمود نواف الشمرى	30863407340	27	\N	55571880	2025-11-28 10:38:57.670719
834	محسن محمد محسن انديله محمد	30863402591	27	\N	66822379	2025-11-28 10:38:57.671038
835	محمد جابر محمد حمد العيده	30963403540	27	\N	55438178	2025-11-28 10:38:57.671339
836	محمد سالم محمد البريص المرى	30863400722	27	\N	77721282	2025-11-28 10:38:57.671642
837	نواف عيسى جمعه الجهبل ضاحى	30763400590	27	\N	66783008	2025-11-28 10:38:57.671954
838	ابراهيم محمد امام بخش صالح	30658600120	28	\N	55177785	2025-11-28 10:38:57.672247
839	جابر ناصر محمد بوسماري المري	30878400041	28	\N	39925979	2025-11-28 10:38:57.672549
840	جارالله سالم حمد سالمين المرى	30863402476	28	\N	55975252	2025-11-28 10:38:57.672861
841	جاسم محمد راشد حمد الشرقى	30863402894	28	\N	50322258	2025-11-28 10:38:57.673176
842	حمد متعب حمد جابر المنخس	30863401383	28	\N	55788106	2025-11-28 10:38:57.673477
843	راشد حمد راشد محسن عبدان	30863402932	28	\N	55401666	2025-11-28 10:38:57.673789
844	سالم حمد سالم العذبه المرى	30863401683	28	\N	33360206	2025-11-28 10:38:57.674096
845	سالم سعيد سالم سعيد الاسود	30763404057	28	\N	33333888	2025-11-28 10:38:57.674405
846	سالم محمد سعيد سالم حمد	30863401614	28	\N	55559104	2025-11-28 10:38:57.674708
847	سعود بليهين حزام حسن القحطانى	30863400434	28	\N	55008466	2025-11-28 10:38:57.675029
848	سعود على راشد محسن عبدان	30763406754	28	\N	55899083	2025-11-28 10:38:57.675333
849	سعيد حمد سعيد قربان الجحيش	30663402386	28	\N	55553101	2025-11-28 10:38:57.675651
850	سعيد سالم محمد مبارك الجهويل	30863401286	28	\N	55569996	2025-11-28 10:38:57.675995
851	سعيد عبدالله على عبدالله ابوشارب	30563401428	28	\N	66628883	2025-11-28 10:38:57.676326
852	سعيد علي سعيد الجربوعي المري	30668200069	28	\N	31442484	2025-11-28 10:38:57.676629
853	شاكر غلام رضا زكريا خان	30658600654	28	\N	55340526	2025-11-28 10:38:57.679464
854	صالح سعيد حسين سعيد السفران	30663403452	28	\N	55382165	2025-11-28 10:38:57.680072
855	صالح محمد صالح البريص المرى	30763405400	28	\N	55899939	2025-11-28 10:38:57.680409
856	عايد ناصر عايد الفريجى الرويلى	30863401977	28	\N	77785858	2025-11-28 10:38:57.680734
857	عبدالرحمن زابت جان زيب جان	30558600911	28	\N	74406002	2025-11-28 10:38:57.68108
858	عبدالعزيز جمل عويلى المقاطى العتيبى	30463404642	28	\N	55988661	2025-11-28 10:38:57.681403
859	عبدالعزيز فهد عبدالله محمد العامرى	30763405350	28	\N	55254697	2025-11-28 10:38:57.681717
860	عبدالله محمد يوسف القريناوى	30799900251	28	\N	55593325	2025-11-28 10:38:57.682032
861	عوض فرحان سعد ال غراب القحطانى	30663403655	28	\N	55511260	2025-11-28 10:38:57.682353
862	فيصل حمد على حمد ملهيه	30863406684	28	\N	55855529	2025-11-28 10:38:57.682802
863	مبارك على مبارك السوداء المرى	30863406182	28	\N	55060019	2025-11-28 10:38:57.683115
864	محمد حمد سعيد قربان الجحيش	30863404618	28	\N	33359922	2025-11-28 10:38:57.683418
865	محمد عبدالله محمد العفيفه المري	30963400075	28	\N	66753135	2025-11-28 10:38:57.683721
866	محمد محسن محمد قائد الرياشي	30788600160	28	\N	55913136	2025-11-28 10:38:57.684036
867	ناصر حمد سعيد سالم هطيل	30863403500	28	\N	55848248	2025-11-28 10:38:57.684339
868	نواف على جارالله العذبه المرى	30663403915	28	\N	55824777	2025-11-28 10:38:57.684641
869	نواف محمد طينان العذبه المرى	30663405994	28	\N	33348888	2025-11-28 10:38:57.684953
870	أحمد سعود	30858600465	29	\N	55591452	2025-11-28 10:38:57.685252
871	جابر عبدالله حمد محمد الزكيبا	30663403052	29	\N	55766608	2025-11-28 10:38:57.685553
872	جابر على جابر البريد المرى	30963401132	29	\N	55000387	2025-11-28 10:38:57.685958
873	حسين محمد ناصر ال حارث اليامى	30863406518	29	\N	70999949	2025-11-28 10:38:57.686264
874	حمد محمد فهد محمد القوبعى	30863405473	29	\N	66985557	2025-11-28 10:38:57.686579
875	حمد هلال محمد هلال هلال	30763402479	29	\N	55833000	2025-11-28 10:38:57.686888
876	خالد محمد اسماعيل غلام نبي البلوشي	30651200004	29	\N	30404181	2025-11-28 10:38:57.687202
877	راشد عبدالله عايد الفريجى الرويلى	30863405887	29	\N	55800430	2025-11-28 10:38:57.687511
878	راشد محمد عبدالله محمد الزكيبا	30663406093	29	\N	66344440	2025-11-28 10:38:57.687831
879	رحبان محمد عايد الفريجى الرويلى	30863404771	29	\N	55804606	2025-11-28 10:38:57.688131
880	سالم مبارك سالم ثوعار المهري	30851200052	29	\N	33213238	2025-11-28 10:38:57.688442
881	سعود معيض عايض ال فطيح القحطانى	30863403885	29	\N	55502655	2025-11-28 10:38:57.688751
882	سعيد راشد حمد البريدى المرى	30863406023	29	\N	66506777	2025-11-28 10:38:57.689104
883	سلطان محمد على البريدى المرى	30963400872	29	\N	55964193	2025-11-28 10:38:57.689407
884	عبدالله احمد كلوش مسلم كده	30563402198	29	\N	55545419	2025-11-28 10:38:57.689722
885	عبدالله على محمد البريص المرى	30763405775	29	\N	55300993	2025-11-28 10:38:57.690038
886	عبدالله ناصر عبدالله الطرابيل البريدى	30563402844	29	\N	66626211	2025-11-28 10:38:57.690348
887	على جابر راشد محمد عظيبه	30863405123	29	\N	66096060	2025-11-28 10:38:57.690661
888	على حمد على راشد المري	30678400017	29	\N	55505735	2025-11-28 10:38:57.690986
889	غيدان حسن علي القحطاني	30868200372	29	\N	31494834	2025-11-28 10:38:57.69146
890	فلاح جبر على محمد الجهمى	30863403897	29	\N	30442121	2025-11-28 10:38:57.691777
891	فهد طالب مسلم بن عقيل النابت	30863402808	29	\N	55562287	2025-11-28 10:38:57.692087
892	محمد بسام بدر محسن فضل	30888600162	29	\N	55205514	2025-11-28 10:38:57.692405
893	محمد جابر محمد البريدى المرى	30763402841	29	\N	55518553	2025-11-28 10:38:57.695848
894	محمد زيد محمد نديله المرى	30663402951	29	\N	0	2025-11-28 10:38:57.696566
895	محمد عبدالله ناصر الهولى النعيمى	30763406872	29	\N	55898948	2025-11-28 10:38:57.697095
896	محمد على حمد هران المرى	30863405065	29	\N	33294040	2025-11-28 10:38:57.702824
897	محمد متعب على العريض المرى	30863400264	29	\N	66721183	2025-11-28 10:38:57.703322
898	مسفر سيف على عبدالله سفران	30963407028	29	\N	55374234	2025-11-28 10:38:57.703716
899	مسفر على مسفر سفران المرى	30663401829	29	\N	33377454	2025-11-28 10:38:57.704162
900	مشعل سعيد سالم جارالله المرى	30863402187	29	\N	33332349	2025-11-28 10:38:57.704612
901	ناصر عبدالهادى فرج مشروم العوير	30863403370	29	\N	55288801	2025-11-28 10:38:57.705042
902	احمد عوض الله حسب الرسول احمد الفكى	30473600729	30	\N	55902040	2025-11-28 10:38:57.705439
903	تويم حمد محمد كليفيخ المنخس	30963400498	30	\N	55844405	2025-11-28 10:38:57.705876
904	حمد جابر جارالله البريد المرى	30863404411	30	\N	66144554	2025-11-28 10:38:57.70627
905	حمد راشد على حمد اليربوعى	30763405674	30	\N	55611661	2025-11-28 10:38:57.706662
906	حمد سعيد محمد ال نوره المرى	30663404688	30	\N	0	2025-11-28 10:38:57.707028
907	خالد شاجع ناصر ال الحارث اليامى	30863401797	30	\N	55817737	2025-11-28 10:38:57.707374
908	راشد بخيت سالم بخيت الابهق	30763406075	30	\N	50409999	2025-11-28 10:38:57.707727
909	راشد جابر سعيد جابر عفيفه	30863403906	30	\N	55821000	2025-11-28 10:38:57.70808
910	راشد على سعيد حديد المرى	30863404603	30	\N	77772764	2025-11-28 10:38:57.708407
911	راكان فيصل منصور محمد الحوبان	30863405576	30	\N	55590052	2025-11-28 10:38:57.708865
912	سالم بخيت سالم بخيت الابهق	30663406010	30	\N	50409999	2025-11-28 10:38:57.709228
913	سالم عبدالله سالم العفيفه المرى	30863401769	30	\N	50004674	2025-11-28 10:38:57.709589
914	سالم عفاس محمد راشد المرى	30863404114	30	\N	33220393	2025-11-28 10:38:57.709954
915	سعيد حمد سعيد البويصم المرى	30763406896	30	\N	66688819	2025-11-28 10:38:57.712279
916	سعيد خالد سالم المهري	30868200029	30	\N	55285979	2025-11-28 10:38:57.712896
917	سليم حمد ناصر محمد المرى	30663405785	30	\N	55331763	2025-11-28 10:38:57.71344
918	عبدالعزيز سالم حمد النهاب المرى	30763403390	30	\N	55506650	2025-11-28 10:38:57.713974
919	عبدالله حمد عبدالله البريدى المرى	30863402507	30	\N	55184999	2025-11-28 10:38:57.714403
920	عبدالله سالم محمد عبدالله عفيفه	30863403733	30	\N	66277007	2025-11-28 10:38:57.714774
921	عبدالهادى جابر على حمد البريد	30963406567	30	\N	55555661	2025-11-28 10:38:57.715463
922	على احمد كلوش مسلم كده	30763401989	30	\N	55545419	2025-11-28 10:38:57.715968
923	على ناصر حمد البريد المرى	30663400119	30	\N	66629978	2025-11-28 10:38:57.716386
924	فهد سعيد على سعيد المرى	30863406647	30	\N	55408222	2025-11-28 10:38:57.71781
925	فيصل محمد جابر عفير المرى	30763407032	30	\N	55526767	2025-11-28 10:38:57.718224
926	محمد ثامر محمد البريدى المرى	30863405818	30	\N	55064114	2025-11-28 10:38:57.7186
927	محمد جابر محمد البريدى المرى	30963406439	30	\N	55655447	2025-11-28 10:38:57.718973
928	محمد خالد حسين عبد صالح	30588600664	30	\N	33221777	2025-11-28 10:38:57.719324
929	محمد سعيد مستور ال الشريف القحطانى	30763403798	30	\N	55222380	2025-11-28 10:38:57.719682
930	محمد على محمد صبيح السنيد	30763405163	30	\N	66666347	2025-11-28 10:38:57.720056
931	محمد غازي محمد صبر	30688600759	30	\N	33906313	2025-11-28 10:38:57.720401
932	ناصر على محمد صبيح السنيد	30663405318	30	\N	66666347	2025-11-28 10:38:57.720837
933	وسام راشد محمد الحسناء المرى	30863401789	30	\N	33322138	2025-11-28 10:38:57.723865
\.


--
-- TOC entry 3571 (class 0 OID 16452)
-- Dependencies: 224
-- Data for Name: subject; Type: TABLE DATA; Schema: public; Owner: adminit
--

COPY public.subject (id, name, code, created_at) FROM stdin;
1	اللغةالعربية	\N	2025-11-28 07:24:02.971712
2	اللغةالانجليزية	\N	2025-11-28 07:24:02.971712
3	الاحياء	\N	2025-11-28 07:24:02.971712
4	الفيزياء	\N	2025-11-28 07:24:02.971712
5	الكيمياء	\N	2025-11-28 07:24:02.971712
6	التربية الإسلامية	\N	2025-11-28 07:24:02.971712
7	الدراسات الاجتماعية	\N	2025-11-28 07:24:02.971712
8	التاريخ	\N	2025-11-28 07:24:02.971712
9	الجغرافيا	\N	2025-11-28 07:24:02.971712
10	التربية البدنية	\N	2025-11-28 07:24:02.971712
11	الرياضيات	\N	2025-11-28 07:24:02.971712
12	المهارات الحياتية	\N	2025-11-28 07:24:02.971712
13	الحاسوب	\N	2025-11-28 07:24:02.971712
14	العلوم	\N	2025-11-28 07:24:02.971712
15	ITC	\N	2026-01-10 19:58:04.829353
\.


--
-- TOC entry 3573 (class 0 OID 16464)
-- Dependencies: 226
-- Data for Name: teacher_subject; Type: TABLE DATA; Schema: public; Owner: adminit
--

COPY public.teacher_subject (id, teacher_id, subject_id, created_at, class_id) FROM stdin;
\.


--
-- TOC entry 3563 (class 0 OID 16392)
-- Dependencies: 216
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: adminit
--

COPY public."user" (id, username, password, role, created_at, national_id, classes, email, emp_id) FROM stdin;
1	admin	scrypt:32768:8:1$jGxy4aFKdYvPiGrp$b71a22c92694cc2f8335df9cbab9b61b43af65f028c730c74c4efff3e5a0bba03d334c82cc30454446e178530e9c2338122c12fca8b8ce71d5ccdab41aacb660	admin	2025-11-28 10:38:57.279163	\N	\N	\N	\N
85	 عبدالعزيز خيرمحمد رجب رمضان رئيسى 	scrypt:32768:8:1$WVu2gmTnl7TkhEPi$3238a9c5fc6902dd5fe9e2416d30282a4911c24149086456310cfbdb714863626a149090c32c531fde6263bea9aa7c5e28204c846b62278b35c42b836c2d80fb	staff	2025-11-28 10:38:57.31652	None       	1,2,3                                                                                               	a.raeissi1305@education.qa                                                                          	\N
86	 اشرف محمود محمد احمد 	scrypt:32768:8:1$VgzE5hq1ctpRztv3$83c01bb313415c484342e7e55f0cecaa77af410738c301195c1999e142264ecd9126504a5054281d693686f824d5495c4ab351bdcc4bc3f06064ebcbdb5684cb	staff	2025-11-28 10:38:57.316815	10000      	1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30                    	a.mohamed14072@education.qa                                                                         	\N
14	أحمد محمود الشيخ	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.288974	None       	1,3,4,5,6                                                                                           	a.elshaikh2001@education.qa                                                                         	\N
2	1	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.282176	\N	\N	\N	\N
3	احمد عبد الله عبد الغني احمد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.283842	\N	\N	\N	\N
4	المختار حدامين	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.284216	\N	\N	\N	\N
5	المعز بالله طه حسين	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.284529	\N	\N	\N	\N
6	إبراهيم أحمد محمد حمودة	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.28483	\N	\N	\N	\N
7	إبراهيم عبد اللطيف البداينه	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.28513	\N	\N	\N	\N
8	إسلام حمدي غنيم	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.285456	\N	\N	\N	\N
9	أحمد عادل عبد الله بكر	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.285758	\N	\N	\N	\N
10	أحمد عزت جبر محمود	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.286779	\N	\N	\N	\N
12	أحمد محمد عباس كرمل	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.287598	\N	\N	\N	\N
13	أحمد محمد عثمان إمام	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.288567	\N	\N	\N	\N
16	أسامة عمر محمد علي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.289644	\N	\N	\N	\N
17	أشرف إبراهيم عبد الله حسين	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.291102	\N	\N	\N	\N
18	أشرف عايد عوض حسين	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.29171	\N	\N	\N	\N
19	أنيس الجيلاني شعبان	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.292198	\N	\N	\N	\N
20	أيمن سيد دسوقي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.292657	\N	\N	\N	\N
21	أيمن عيد عبد العظيم	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.293104	\N	\N	\N	\N
22	جلال محمد نجيب القاسمي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.293485	\N	\N	\N	\N
23	حجازي علي أحمد عمري	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.293829	\N	\N	\N	\N
24	حمدي عبد الجيد سالم مقلد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.294168	\N	\N	\N	\N
25	خالد السيد السطوحى سرور	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.294522	\N	\N	\N	\N
26	خالد صالح إدريس عياد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.294861	\N	\N	\N	\N
27	خالد محمد سيد محمد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.295203	\N	\N	\N	\N
28	رمضان ربيع خضري سليمان	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.29552	\N	\N	\N	\N
15	أركان أحمد حسين عنانزه	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.289327	\N	1,3,5,7,9                                                                                           	\N	\N
11	أحمد عطا موسى	scrypt:32768:8:1$No9r8QYOQjjNOf4z$51584af458e009fdf64f74567a8153ff817531e1e304b7a3bf22b2ffabd0889ae94910f2854de5c5a334777fe0aeeb39edd0201a30dd447b3ae7d1c0fef8e8f6	teacher	2025-11-28 10:38:57.287204	None       	1,2,3,4,5,6,7                                                                                       	a.muosa1004@education.qa                                                                            	\N
29	زكريا قصاب	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.295829	\N	\N	\N	\N
30	سامر عبد الله سعد الجابر	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.296125	\N	\N	\N	\N
31	سعيد كمال عبد الحميد محمد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.296413	\N	\N	\N	\N
32	سيد ربيع عبد الفتاح جنيدي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.296707	\N	\N	\N	\N
33	شجاع علي محمد العابد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.297283	\N	\N	\N	\N
34	صبري بن رضى العمري	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.297605	\N	\N	\N	\N
35	عامر صالح التركي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.29791	\N	\N	\N	\N
36	عبد الرحمن محمد عبد المولى 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.298206	\N	\N	\N	\N
37	عبد الكريم محمد سالم نوفل	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.298505	\N	\N	\N	\N
38	عبد الوهاب جمال الرجوب	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.298798	\N	\N	\N	\N
39	عروة حسين محب الدين	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.299104	\N	\N	\N	\N
40	عصام محمد نعمان قرش	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.299853	\N	\N	\N	\N
41	عطية إبراهيم شلبي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.300177	\N	\N	\N	\N
42	علاء الدين محمود جمعه عبيد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.300469	\N	\N	\N	\N
43	علي ناصري	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.300776	\N	\N	\N	\N
44	عماد عزب سليمان	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.301076	\N	\N	\N	\N
45	عمر يونس غندور	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.301372	\N	\N	\N	\N
46	عيد أحمد جنيدي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.30167	\N	\N	\N	\N
47	غسان غازي بدر العمري	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.302006	\N	\N	\N	\N
48	قنديل أحمد قنديل توفيق	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.302301	\N	\N	\N	\N
49	مالك كنجو النجار	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.302587	\N	\N	\N	\N
50	ماهر محمد عامودي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.302876	\N	\N	\N	\N
51	محمد  أحمد مصطفى الكواليني 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.303155	\N	\N	\N	\N
52	محمد احمد البدوي البديوي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.303453	\N	\N	\N	\N
53	محمد السعيد إبراهيم حماد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.303756	\N	\N	\N	\N
54	محمد السيد العربي جبران	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.304075	\N	\N	\N	\N
55	محمد إبراهيم إبراهيم فرج ندا	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.304381	\N	\N	\N	\N
56	محمد أيوب محمود فتح الباب	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.304684	\N	\N	\N	\N
57	محمد جهاد محمد عصفور	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.305299	\N	\N	\N	\N
58	محمد حافظ محمد عبد الخالق	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.305657	\N	\N	\N	\N
59	محمد حفيض علي ال صفور المري	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.306003	\N	\N	\N	\N
60	محمد عبد الحميد عبد الرحيم الشاقلدي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.306402	\N	\N	\N	\N
61	محمد عبد الرحمن الزين	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.306789	\N	\N	\N	\N
62	محمد عبد الرحمن حسن 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.307153	\N	\N	\N	\N
63	محمد عبد المنعم محمد السيد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.307473	\N	\N	\N	\N
64	محمد عزام نمر العمر	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.307877	\N	\N	\N	\N
65	محمد علي العبود أبو العناز	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.308232	\N	\N	\N	\N
66	محمد محمود محمد اللقاني	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.308573	\N	\N	\N	\N
67	محمد ملاحي طافش	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.308958	\N	\N	\N	\N
68	محمد يوسف الصفوري	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.310411	\N	\N	\N	\N
69	محمود درويش مصطفى الغفاري	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.3111	\N	\N	\N	\N
70	محمود مبروك السيد عيد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.311425	\N	\N	\N	\N
71	محمود محمد عبد المحسن حداد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.31173	\N	\N	\N	\N
72	مصطفى قاسم أحمد الذروي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.312029	\N	\N	\N	\N
73	مهند حسن محمود الزعبي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.312642	\N	\N	\N	\N
74	مهند محمد حسين خفاجه	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.312988	\N	\N	\N	\N
75	هاني محمد حسين نصار	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.313448	\N	\N	\N	\N
76	هشام أحمد محمد الجزار	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.313777	\N	\N	\N	\N
77	هيثم رجا عبيد الحنيفات	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.314076	\N	\N	\N	\N
78	وسام كمال نصر	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.314369	\N	\N	\N	\N
79	ياسر السيد أحمد أحمد	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.314666	\N	\N	\N	\N
80	ياسر محمد عبد الحميد السمان	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.314968	\N	\N	\N	\N
81	ياسين بن الحبيب بريكي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.315277	\N	\N	\N	\N
82	يوسف ضو حامدي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.315572	\N	\N	\N	\N
83	يوسف عبه جي	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.315878	\N	\N	\N	\N
84	 مؤيد اسعد حسين دناوي 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	teacher	2025-11-28 10:38:57.316237	\N	\N	\N	\N
87	 الحسين  سوسي 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.317112	\N	\N	\N	\N
88	 جواد  الاطرش 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.317426	\N	\N	\N	\N
89	 حسن عمر حسن عثمان 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.317709	\N	\N	\N	\N
90	 سعيد  يمين 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.318016	\N	\N	\N	\N
91	 محمد جباره عجب سيدو فضل المولى 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.318299	\N	\N	\N	\N
92	 محمد زين العابدين محمد عوض الله رزق 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.318581	\N	\N	\N	\N
93	 محمد عبد الرؤوف علي القصاص 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.318883	\N	\N	\N	\N
94	 محمود عبدالوهاب احمد مصلح 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.319178	\N	\N	\N	\N
95	 هشام  لعموري 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.319546	\N	\N	\N	\N
96	 ياسر فوزي محمد درغام 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.31985	\N	\N	\N	\N
97	 غانم راجح حنظل الفهيده المري 	scrypt:32768:8:1$0gLeMMT7o1dPcyTR$d923b0a638608ad435488a7d276cb4ec72e63ca4367555739162acf08e866b35de0797a0beb189b0d8abec5fdf77dac1582f958856a877d89c253cda23d96170	staff	2025-11-28 10:38:57.320131	\N	\N	\N	\N
\.


--
-- TOC entry 3588 (class 0 OID 0)
-- Dependencies: 227
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: adminit
--

SELECT pg_catalog.setval('public.attendance_id_seq', 582, true);


--
-- TOC entry 3589 (class 0 OID 0)
-- Dependencies: 219
-- Name: period_id_seq; Type: SEQUENCE SET; Schema: public; Owner: adminit
--

SELECT pg_catalog.setval('public.period_id_seq', 11, true);


--
-- TOC entry 3590 (class 0 OID 0)
-- Dependencies: 217
-- Name: school_class_id_seq; Type: SEQUENCE SET; Schema: public; Owner: adminit
--

SELECT pg_catalog.setval('public.school_class_id_seq', 1, false);


--
-- TOC entry 3591 (class 0 OID 0)
-- Dependencies: 221
-- Name: student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: adminit
--

SELECT pg_catalog.setval('public.student_id_seq', 1, false);


--
-- TOC entry 3592 (class 0 OID 0)
-- Dependencies: 223
-- Name: subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: adminit
--

SELECT pg_catalog.setval('public.subject_id_seq', 1, false);


--
-- TOC entry 3593 (class 0 OID 0)
-- Dependencies: 225
-- Name: teacher_subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: adminit
--

SELECT pg_catalog.setval('public.teacher_subject_id_seq', 1, false);


--
-- TOC entry 3594 (class 0 OID 0)
-- Dependencies: 215
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: adminit
--

SELECT pg_catalog.setval('public.user_id_seq', 2, true);


--
-- TOC entry 3400 (class 2606 OID 16494)
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- TOC entry 3402 (class 2606 OID 16496)
-- Name: attendance attendance_student_id_date_period_key; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_student_id_date_period_key UNIQUE (student_id, date, period);


--
-- TOC entry 3378 (class 2606 OID 16425)
-- Name: period period_period_num_class_id_teacher_id_key; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.period
    ADD CONSTRAINT period_period_num_class_id_teacher_id_key UNIQUE (period_num, class_id, teacher_id);


--
-- TOC entry 3380 (class 2606 OID 16423)
-- Name: period period_pkey; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.period
    ADD CONSTRAINT period_pkey PRIMARY KEY (id);


--
-- TOC entry 3373 (class 2606 OID 16410)
-- Name: school_class school_class_name_key; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.school_class
    ADD CONSTRAINT school_class_name_key UNIQUE (name);


--
-- TOC entry 3375 (class 2606 OID 16408)
-- Name: school_class school_class_pkey; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.school_class
    ADD CONSTRAINT school_class_pkey PRIMARY KEY (id);


--
-- TOC entry 3385 (class 2606 OID 16443)
-- Name: student student_pkey; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_pkey PRIMARY KEY (id);


--
-- TOC entry 3387 (class 2606 OID 16445)
-- Name: student student_roll_number_key; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_roll_number_key UNIQUE (roll_number);


--
-- TOC entry 3389 (class 2606 OID 16462)
-- Name: subject subject_code_key; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_code_key UNIQUE (code);


--
-- TOC entry 3391 (class 2606 OID 16460)
-- Name: subject subject_name_key; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_name_key UNIQUE (name);


--
-- TOC entry 3393 (class 2606 OID 16458)
-- Name: subject subject_pkey; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.subject
    ADD CONSTRAINT subject_pkey PRIMARY KEY (id);


--
-- TOC entry 3396 (class 2606 OID 16470)
-- Name: teacher_subject teacher_subject_pkey; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.teacher_subject
    ADD CONSTRAINT teacher_subject_pkey PRIMARY KEY (id);


--
-- TOC entry 3398 (class 2606 OID 16472)
-- Name: teacher_subject teacher_subject_teacher_id_subject_id_key; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.teacher_subject
    ADD CONSTRAINT teacher_subject_teacher_id_subject_id_key UNIQUE (teacher_id, subject_id);


--
-- TOC entry 3382 (class 2606 OID 16528)
-- Name: period unique_day_period; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.period
    ADD CONSTRAINT unique_day_period UNIQUE (day_of_week, period_num);


--
-- TOC entry 3369 (class 2606 OID 16398)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 3371 (class 2606 OID 16400)
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- TOC entry 3403 (class 1259 OID 16516)
-- Name: idx_attendance_class_id; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_attendance_class_id ON public.attendance USING btree (class_id);


--
-- TOC entry 3404 (class 1259 OID 16512)
-- Name: idx_attendance_date_class; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_attendance_date_class ON public.attendance USING btree (date, class_id);


--
-- TOC entry 3405 (class 1259 OID 16515)
-- Name: idx_attendance_period; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_attendance_period ON public.attendance USING btree (period);


--
-- TOC entry 3406 (class 1259 OID 16513)
-- Name: idx_attendance_period_class_teacher; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_attendance_period_class_teacher ON public.attendance USING btree (period, class_id, teacher_id);


--
-- TOC entry 3407 (class 1259 OID 16514)
-- Name: idx_attendance_student_date; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_attendance_student_date ON public.attendance USING btree (student_id, date);


--
-- TOC entry 3408 (class 1259 OID 16522)
-- Name: idx_attendance_student_date_period; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_attendance_student_date_period ON public.attendance USING btree (student_id, date, period);


--
-- TOC entry 3409 (class 1259 OID 16517)
-- Name: idx_attendance_teacher_id; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_attendance_teacher_id ON public.attendance USING btree (teacher_id);


--
-- TOC entry 3376 (class 1259 OID 16518)
-- Name: idx_period_class_teacher; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_period_class_teacher ON public.period USING btree (class_id, teacher_id);


--
-- TOC entry 3383 (class 1259 OID 16519)
-- Name: idx_student_class; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_student_class ON public.student USING btree (class_id);


--
-- TOC entry 3394 (class 1259 OID 16521)
-- Name: idx_teacher_subject; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_teacher_subject ON public.teacher_subject USING btree (teacher_id, subject_id);


--
-- TOC entry 3367 (class 1259 OID 16520)
-- Name: idx_user_username; Type: INDEX; Schema: public; Owner: adminit
--

CREATE INDEX idx_user_username ON public."user" USING btree (username);


--
-- TOC entry 3416 (class 2606 OID 16502)
-- Name: attendance attendance_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.school_class(id) ON DELETE CASCADE;


--
-- TOC entry 3417 (class 2606 OID 16497)
-- Name: attendance attendance_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.student(id) ON DELETE CASCADE;


--
-- TOC entry 3418 (class 2606 OID 16507)
-- Name: attendance attendance_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- TOC entry 3411 (class 2606 OID 16426)
-- Name: period period_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.period
    ADD CONSTRAINT period_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.school_class(id) ON DELETE CASCADE;


--
-- TOC entry 3412 (class 2606 OID 16431)
-- Name: period period_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.period
    ADD CONSTRAINT period_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- TOC entry 3410 (class 2606 OID 16411)
-- Name: school_class school_class_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.school_class
    ADD CONSTRAINT school_class_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public."user"(id) ON DELETE SET NULL;


--
-- TOC entry 3413 (class 2606 OID 16446)
-- Name: student student_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.student
    ADD CONSTRAINT student_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.school_class(id) ON DELETE CASCADE;


--
-- TOC entry 3414 (class 2606 OID 16478)
-- Name: teacher_subject teacher_subject_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.teacher_subject
    ADD CONSTRAINT teacher_subject_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subject(id) ON DELETE CASCADE;


--
-- TOC entry 3415 (class 2606 OID 16473)
-- Name: teacher_subject teacher_subject_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: adminit
--

ALTER TABLE ONLY public.teacher_subject
    ADD CONSTRAINT teacher_subject_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public."user"(id) ON DELETE CASCADE;


-- Completed on 2026-01-21 23:45:43 +03

--
-- PostgreSQL database dump complete
--

\unrestrict elZ0B7wgDy0x4Q4ewcS5fA1A4fj1EN0bbceYmmdEQVqiLKbu9YpsQ6qI1p2qrez

