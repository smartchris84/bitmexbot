--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.5
-- Dumped by pg_dump version 10.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: configs; Type: TABLE; Schema: public; Owner: kirill
--

CREATE TABLE configs (
    "IS_RUNNING" boolean DEFAULT false,
    "PERCENT_TO_TRADE" double precision DEFAULT '0'::double precision,
    "API_KEY" text DEFAULT 'none'::text,
    "API_SECRET" text DEFAULT 'none'::text,
    "TIMEFRAME" text DEFAULT '1Min'::text,
    "LEVERAGE" double precision DEFAULT '15'::double precision,
    "SL_PERCENT" double precision DEFAULT '0'::double precision,
    "TP_PERCENT" double precision DEFAULT '0'::double precision,
    "UPDATED" boolean DEFAULT false,
    "RSI_TOP" double precision DEFAULT '75'::double precision,
    "RSI_BOT" double precision DEFAULT '25'::double precision
);


ALTER TABLE configs OWNER TO kirill;

--
-- Name: trade; Type: TABLE; Schema: public; Owner: kirill
--

CREATE TABLE trade (
    symbol text DEFAULT 'BTC/USD'::text NOT NULL,
    longed boolean DEFAULT false,
    shorted boolean DEFAULT false,
    timeframe text,
    sl_lvl double precision DEFAULT '-1'::double precision,
    tp_lvl double precision DEFAULT '-1'::double precision,
    amount double precision DEFAULT '0'::double precision,
    date_open timestamp without time zone,
    price_open double precision DEFAULT '0'::double precision,
    last_price_close double precision DEFAULT '0'::double precision
);


ALTER TABLE trade OWNER TO kirill;

--
-- Data for Name: configs; Type: TABLE DATA; Schema: public; Owner: kirill
--

COPY configs ("IS_RUNNING", "PERCENT_TO_TRADE", "API_KEY", "API_SECRET", "TIMEFRAME", "LEVERAGE", "SL_PERCENT", "TP_PERCENT", "UPDATED", "RSI_TOP", "RSI_BOT") FROM stdin;
f	0	GZcckbvstvYFYYfMziEAMXaP	EmBaG_wG6LmbO2Pab057iCHiQxYJoW32PIzSJnKwc7hv0tBK	1Min	15	0	0	f	75	25
\.


--
-- Data for Name: trade; Type: TABLE DATA; Schema: public; Owner: kirill
--

COPY trade (symbol, longed, shorted, timeframe, sl_lvl, tp_lvl, amount, date_open, price_open, last_price_close) FROM stdin;
BTC/USD	f	f	\N	-1	-1	0	\N	0	0
\.


--
-- Name: trade trade_pkey; Type: CONSTRAINT; Schema: public; Owner: kirill
--

ALTER TABLE ONLY trade
    ADD CONSTRAINT trade_pkey PRIMARY KEY (symbol);


--
-- PostgreSQL database dump complete
--

