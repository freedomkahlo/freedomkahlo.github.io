<?php
$dbhandle = sqlite_open('../../../db.sqlite3', 0666, $error);
if (!$dbhandle) die ($error);

$text = $mysqli->real_escape_string($_GET['term']);
 



$query = "SELECT users FROM bands WHERE name LIKE '%$text%' ORDER BY name ASC";
$result = $mysqli->query($query);
$json = '[';
$first = true;
while($row = $result->fetch_assoc())
{
    if (!$first) { $json .=  ','; } else { $first = false; }
    $json .= '{"value":"'.$row['name'].'"}';
}
$json .= ']';
echo $json;