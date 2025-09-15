pkg load database
conn = pq_connect(setdbopts('dbname','postgres','host','localhost','port','5432','user','postgres','password','koala'));
N=pq_exec_params(conn, "INSERT INTO test VALUES ('12', 'Texto Prueba', 1005 );")
N=pq_exec_params(conn, "SELECT * FROM test;");
disp(N)
