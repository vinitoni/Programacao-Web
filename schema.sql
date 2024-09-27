CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    nome TEXT NOT NULL,
    data_criacao TEXT NOT NULL,
    status TEXT CHECK( status IN ('ativo','bloqueado') ) NOT NULL DEFAULT 'ativo',
    data_ultima_atualizacao TEXT
);
UPDATE usuarios SET data_ultima_atualizacao = ? WHERE id = ?
