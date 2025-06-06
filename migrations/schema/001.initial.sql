CREATE TABLE "user" (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    patronymic VARCHAR(50),
    card_number VARCHAR(20) NOT NULL UNIQUE,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

COMMENT ON TABLE "user" IS 'Представляет информацию о пользователе системы.';
COMMENT ON COLUMN "user".id IS 'Уникальный ID пользователя.';
COMMENT ON COLUMN "user".first_name IS 'Имя пользователя.';
COMMENT ON COLUMN "user".last_name IS 'Фамилия пользователя.';
COMMENT ON COLUMN "user".patronymic IS 'Отчество пользователя.';
COMMENT ON COLUMN "user".card_number IS 'Уникальный номер карты пользователя.';
COMMENT ON COLUMN "user".balance IS 'Текущее количество денег на балансе пользователя.';

CREATE TABLE car (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    license_plate VARCHAR(9) NOT NULL UNIQUE,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE car IS 'Представляет информацию об автомобиле, связанном с пользователем.';
COMMENT ON COLUMN car.id IS 'Уникальный ID автомобиля.';
COMMENT ON COLUMN car.user_id IS 'ID пользователя, которому принадлежит автомобиль.';
COMMENT ON COLUMN car.license_plate IS 'Уникальный номерной знак автомобиля. Максимальная длина — 9 символов.';

CREATE TABLE car_passage (
    id BIGSERIAL PRIMARY KEY,
    car_id BIGINT NOT NULL,
    passage_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- 1: въезд (entry), 2: выезд (exit)
    passage_type INT NOT NULL CHECK (passage_type IN (1, 2)),
    CONSTRAINT fk_car
        FOREIGN KEY(car_id)
        REFERENCES car(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE car_passage IS 'Запись о проезде автомобиля через контрольную точку.';
COMMENT ON COLUMN car_passage.id IS 'Уникальный ID проезда.';
COMMENT ON COLUMN car_passage.car_id IS 'ID автомобиля, совершившего проезд.';
COMMENT ON COLUMN car_passage.passage_time IS 'Время совершения проезда.';
COMMENT ON COLUMN car_passage.passage_type IS 'Тип проезда: 1 для въезда, 2 для выезда.';

CREATE TABLE transaction (
    id BIGSERIAL PRIMARY KEY,
    passage_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_passage
        FOREIGN KEY(passage_id)
        REFERENCES car_passage(id)
        ON DELETE CASCADE
);

COMMENT ON TABLE transaction IS 'Запись о финансовой транзакции, связанной с проездом автомобиля.';
COMMENT ON COLUMN transaction.id IS 'Уникальный ID транзакции.';
COMMENT ON COLUMN transaction.passage_id IS 'ID проезда, к которому относится транзакция.';
COMMENT ON COLUMN transaction.amount IS 'Объем списанных средств.';
