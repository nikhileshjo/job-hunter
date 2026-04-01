from sqlalchemy import create_engine
from sqlalchemy import text

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

with engine.connect() as conn:
    r1 = conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    r2 = conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    conn.commit()

print(r1)
print(r2)