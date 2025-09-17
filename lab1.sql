--
-- PostgreSQL database dump
--

\restrict N8TvgMMkOCcAgUpEl6pHpzavnOnNNxgVy56fYbFiSM4qWqI2X9BPBXzSb8lkYjS

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2025-09-17 13:06:40

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

--
-- TOC entry 12 (class 2615 OID 16566)
-- Name: auth; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA auth;


ALTER SCHEMA auth OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 241 (class 1259 OID 16582)
-- Name: LoanJournal; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth."LoanJournal" (
    loan_id integer NOT NULL,
    id_reader integer NOT NULL,
    id_book integer NOT NULL,
    loan_date date NOT NULL,
    return_date date
);


ALTER TABLE auth."LoanJournal" OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16572)
-- Name: author; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.author (
    author_id integer NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(50)
);


ALTER TABLE auth.author OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 16577)
-- Name: book; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.book (
    book_id integer NOT NULL,
    name character varying(50) NOT NULL,
    pages integer NOT NULL,
    year_published integer NOT NULL,
    id_author integer NOT NULL
);


ALTER TABLE auth.book OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 16587)
-- Name: reader; Type: TABLE; Schema: auth; Owner: postgres
--

CREATE TABLE auth.reader (
    reader_id integer NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(50)
);


ALTER TABLE auth.reader OWNER TO postgres;

--
-- TOC entry 4867 (class 0 OID 16582)
-- Dependencies: 241
-- Data for Name: LoanJournal; Type: TABLE DATA; Schema: auth; Owner: postgres
--

COPY auth."LoanJournal" (loan_id, id_reader, id_book, loan_date, return_date) FROM stdin;
1	1	2	2025-09-01	2025-09-10
2	2	1	2025-09-05	2025-09-15
3	3	3	2025-09-07	2025-09-15
\.


--
-- TOC entry 4865 (class 0 OID 16572)
-- Dependencies: 239
-- Data for Name: author; Type: TABLE DATA; Schema: auth; Owner: postgres
--

COPY auth.author (author_id, first_name, last_name, email) FROM stdin;
2	Olena	Shevchenko	olena.shev@gmail.com
3	Mykola	Kovalenko	mykola.k@gmail.com
1	Ivan	Petrenko	ivan.petrenko@gmail.com
\.


--
-- TOC entry 4866 (class 0 OID 16577)
-- Dependencies: 240
-- Data for Name: book; Type: TABLE DATA; Schema: auth; Owner: postgres
--

COPY auth.book (book_id, name, pages, year_published, id_author) FROM stdin;
1	Programming Basics	250	2020	1
2	Modern Art	150	2018	2
3	Physics Fundamentals	300	2021	3
4	C++	200	2019	1
\.


--
-- TOC entry 4868 (class 0 OID 16587)
-- Dependencies: 242
-- Data for Name: reader; Type: TABLE DATA; Schema: auth; Owner: postgres
--

COPY auth.reader (reader_id, first_name, last_name, email) FROM stdin;
1	Anna	Melnyk	anna.melnyk@gmail.com
2	Petro	Ivanov	petro.ivanov@gmail.com
3	Kateryna	Bondar	katya.bondar@gmail.com
\.


--
-- TOC entry 4707 (class 2606 OID 16586)
-- Name: LoanJournal LoanJournal_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth."LoanJournal"
    ADD CONSTRAINT "LoanJournal_pkey" PRIMARY KEY (loan_id);


--
-- TOC entry 4697 (class 2606 OID 16576)
-- Name: author author_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.author
    ADD CONSTRAINT author_pkey PRIMARY KEY (author_id);


--
-- TOC entry 4703 (class 2606 OID 16581)
-- Name: book book_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.book
    ADD CONSTRAINT book_pkey PRIMARY KEY (book_id);


--
-- TOC entry 4699 (class 2606 OID 16624)
-- Name: author email; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.author
    ADD CONSTRAINT email UNIQUE (email);


--
-- TOC entry 4709 (class 2606 OID 16632)
-- Name: reader email_reader; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.reader
    ADD CONSTRAINT email_reader UNIQUE (email);


--
-- TOC entry 4701 (class 2606 OID 16626)
-- Name: author last_name; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.author
    ADD CONSTRAINT last_name UNIQUE (last_name);


--
-- TOC entry 4711 (class 2606 OID 16630)
-- Name: reader last_name_reader; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.reader
    ADD CONSTRAINT last_name_reader UNIQUE (last_name);


--
-- TOC entry 4705 (class 2606 OID 16628)
-- Name: book name; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.book
    ADD CONSTRAINT name UNIQUE (name);


--
-- TOC entry 4713 (class 2606 OID 16591)
-- Name: reader reader_pkey; Type: CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.reader
    ADD CONSTRAINT reader_pkey PRIMARY KEY (reader_id);


--
-- TOC entry 4716 (class 2606 OID 16602)
-- Name: LoanJournal LoanJournal_id_book_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth."LoanJournal"
    ADD CONSTRAINT "LoanJournal_id_book_fkey" FOREIGN KEY (id_book) REFERENCES auth.book(book_id) NOT VALID;


--
-- TOC entry 4717 (class 2606 OID 16618)
-- Name: LoanJournal LoanJournal_id_book_fkey1; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth."LoanJournal"
    ADD CONSTRAINT "LoanJournal_id_book_fkey1" FOREIGN KEY (id_book) REFERENCES auth.book(book_id) NOT VALID;


--
-- TOC entry 4718 (class 2606 OID 16597)
-- Name: LoanJournal LoanJournal_id_reader_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth."LoanJournal"
    ADD CONSTRAINT "LoanJournal_id_reader_fkey" FOREIGN KEY (id_reader) REFERENCES auth.reader(reader_id) NOT VALID;


--
-- TOC entry 4719 (class 2606 OID 16613)
-- Name: LoanJournal LoanJournal_id_reader_fkey1; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth."LoanJournal"
    ADD CONSTRAINT "LoanJournal_id_reader_fkey1" FOREIGN KEY (id_reader) REFERENCES auth.reader(reader_id) NOT VALID;


--
-- TOC entry 4714 (class 2606 OID 16592)
-- Name: book book_id_author_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.book
    ADD CONSTRAINT book_id_author_fkey FOREIGN KEY (id_author) REFERENCES auth.author(author_id) NOT VALID;


--
-- TOC entry 4715 (class 2606 OID 16608)
-- Name: book book_id_author_fkey1; Type: FK CONSTRAINT; Schema: auth; Owner: postgres
--

ALTER TABLE ONLY auth.book
    ADD CONSTRAINT book_id_author_fkey1 FOREIGN KEY (id_author) REFERENCES auth.author(author_id) NOT VALID;


-- Completed on 2025-09-17 13:06:40

--
-- PostgreSQL database dump complete
--

\unrestrict N8TvgMMkOCcAgUpEl6pHpzavnOnNNxgVy56fYbFiSM4qWqI2X9BPBXzSb8lkYjS

