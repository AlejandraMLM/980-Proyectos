pkg load database
conn = pq_connect(setdbopts('dbname','postgres','host','localhost ','port','5432','user','postgres','password','koala'));
N=pq_exec_params(conn, "INSERT INTO redes VALUES ('Carlos', 201400524);");
N=pq_exec_params(conn, "SELECT * FROM redes;");
disp(N)
