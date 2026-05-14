--
-- PostgreSQL database dump
--

\restrict Ejuzj2rRXB504XAmUZyyPmgO6TjuKg3kOnRLgAFaDgwZumL1u1Pi0PrkpzCYYKv

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-05-15 00:48:48

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
-- TOC entry 228 (class 1259 OID 16985)
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    img_path text NOT NULL,
    title text
);


ALTER TABLE public.images OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16984)
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.images_id_seq OWNER TO postgres;

--
-- TOC entry 5033 (class 0 OID 0)
-- Dependencies: 227
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- TOC entry 229 (class 1259 OID 16995)
-- Name: pereval_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pereval_images (
    pereval_id integer NOT NULL,
    image_id integer NOT NULL
);


ALTER TABLE public.pereval_images OWNER TO postgres;

--
-- TOC entry 4874 (class 2604 OID 16988)
-- Name: images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- TOC entry 4876 (class 2606 OID 16994)
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- TOC entry 4878 (class 2606 OID 17001)
-- Name: pereval_images pereval_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_images
    ADD CONSTRAINT pereval_images_pkey PRIMARY KEY (pereval_id, image_id);


--
-- TOC entry 4879 (class 2606 OID 17007)
-- Name: pereval_images pereval_images_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_images
    ADD CONSTRAINT pereval_images_image_id_fkey FOREIGN KEY (image_id) REFERENCES public.images(id) ON DELETE CASCADE;


--
-- TOC entry 4880 (class 2606 OID 17002)
-- Name: pereval_images pereval_images_pereval_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pereval_images
    ADD CONSTRAINT pereval_images_pereval_id_fkey FOREIGN KEY (pereval_id) REFERENCES public.pereval_added(id) ON DELETE CASCADE;


-- Completed on 2026-05-15 00:48:48

--
-- PostgreSQL database dump complete
--

\unrestrict Ejuzj2rRXB504XAmUZyyPmgO6TjuKg3kOnRLgAFaDgwZumL1u1Pi0PrkpzCYYKv

