--
-- PostgreSQL database dump
--

\restrict mGumiXK3rTihAuUSs5dHeYAg2xV591Xpjd5yLNZVUKRkDokdee3VNo7W1RsrSeB

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-05-15 00:42:05

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
-- TOC entry 222 (class 1259 OID 16935)
-- Name: coords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.coords (
    id integer NOT NULL,
    latitude numeric(10,6) NOT NULL,
    longitude numeric(10,6) NOT NULL,
    height integer
);


ALTER TABLE public.coords OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16934)
-- Name: coords_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.coords_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coords_id_seq OWNER TO postgres;

--
-- TOC entry 5039 (class 0 OID 0)
-- Dependencies: 221
-- Name: coords_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.coords_id_seq OWNED BY public.coords.id;


--
-- TOC entry 224 (class 1259 OID 16945)
-- Name: levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.levels (
    id integer NOT NULL,
    winter text,
    summer text,
    autumn text,
    spring text
);


ALTER TABLE public.levels OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16944)
-- Name: levels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.levels_id_seq OWNER TO postgres;

--
-- TOC entry 5040 (class 0 OID 0)
-- Dependencies: 223
-- Name: levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.levels_id_seq OWNED BY public.levels.id;


--
-- TOC entry 226 (class 1259 OID 16955)
-- Name: pereval_added; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pereval_added (
    id integer NOT NULL,
    date_added timestamp without time zone DEFAULT now(),
    beauty_title text,
    title text NOT NULL,
    other_titles text,
    connect text,
    add_time timestamp without time zone,
    status text DEFAULT 'new'::text NOT NULL,
    user_id integer,
    coord_id integer,
    level_id integer,
    CONSTRAINT pereval_added_status_check CHECK ((status = ANY (ARRAY['new'::text, 'pending'::text, 'accepted'::text, 'rejected'::text])))
);


ALTER TABLE public.pereval_added OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16954)
-- Name: pereval_added_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pereval_added_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pereval_added_id_seq OWNER TO postgres;

--
-- TOC entry 5041 (class 0 OID 0)
-- Dependencies: 225
-- Name: pereval_added_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pereval_added_id_seq OWNED BY public.pereval_added.id;


--
-- TOC entry 219 (class 1259 OID 16921)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4868 (class 2604 OID 16938)
-- Name: coords id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coords ALTER COLUMN id SET DEFAULT nextval('public.coords_id_seq'::regclass);


--
-- TOC entry 4869 (class 2604 OID 16948)
-- Name: levels id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.levels ALTER COLUMN id SET DEFAULT nextval('public.levels_id_seq'::regclass);


--
-- TOC entry 4870 (class 2604 OID 16958)
-- Name: pereval_added id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added ALTER COLUMN id SET DEFAULT nextval('public.pereval_added_id_seq'::regclass);


--
-- TOC entry 4879 (class 2606 OID 16943)
-- Name: coords coords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.coords
    ADD CONSTRAINT coords_pkey PRIMARY KEY (id);


--
-- TOC entry 4881 (class 2606 OID 16953)
-- Name: levels levels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.levels
    ADD CONSTRAINT levels_pkey PRIMARY KEY (id);


--
-- TOC entry 4883 (class 2606 OID 16968)
-- Name: pereval_added pereval_added_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added
    ADD CONSTRAINT pereval_added_pkey PRIMARY KEY (id);


--
-- TOC entry 4884 (class 2606 OID 16974)
-- Name: pereval_added pereval_added_coord_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added
    ADD CONSTRAINT pereval_added_coord_id_fkey FOREIGN KEY (coord_id) REFERENCES public.coords(id) ON DELETE CASCADE;


--
-- TOC entry 4885 (class 2606 OID 16979)
-- Name: pereval_added pereval_added_level_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added
    ADD CONSTRAINT pereval_added_level_id_fkey FOREIGN KEY (level_id) REFERENCES public.levels(id) ON DELETE CASCADE;


--
-- TOC entry 4886 (class 2606 OID 16969)
-- Name: pereval_added pereval_added_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_added
    ADD CONSTRAINT pereval_added_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


-- Completed on 2026-05-15 00:42:05

--
-- PostgreSQL database dump complete
--

\unrestrict mGumiXK3rTihAuUSs5dHeYAg2xV591Xpjd5yLNZVUKRkDokdee3VNo7W1RsrSeB

