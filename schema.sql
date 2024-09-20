CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nome TEXT NOT NULL,
    data_criacao TEXT NOT NULL,  -- Armazena a data como string no formato ISO8601
    status TEXT CHECK( status IN ('ativo','bloqueado') ) NOT NULL DEFAULT 'ativo',
    data_ultima_atualizacao TEXT  -- Pode ser nulo na criação, preenchido em atualizações
);
