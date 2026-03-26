CREATE DATABASE HipoteseCapital;

CREATE TABLE Ativos (
    Ticker VARCHAR(255) NOT NULL,
    EmpresaAtivo VARCHAR(20) NOT NULL,
    SetorAtuacaoEmpresa VARCHAR(255) NOT NULL,
    SegmentoAtuacaoEmpresa VARCHAR(255) NOT NULL,
    ResumoEmpresa VARCHAR(2000) NOT NULL,
    PRIMARY KEY (Ticker)
);

CREATE TABLE (
    DataConsulta DATE NOT NULL,
    Ticker VARCHAR(20) NOT NULL,
    P/L
)