<?php
// Dr. Qaria Mini AI outside watcher. Runs from cron on the Hostinger web hosting, away from the main server.
// E-mails only when something stays down for two rounds, and again when it comes back. No AI, no accounts, no secrets.
// Command line only; .htaccess also blocks this folder from the web. --test sends one e-mail with the current state.
if (php_sapi_name() !== 'cli') { http_response_code(404); exit; }

$to = 'sale@njmcmedicsupp.com';
$checks = [
    'Dr. Qaria Mini AI (fails if its checker stopped)' => 'https://panel.187-127-158-97.sslip.io/watch',
    'NJMC website' => 'https://njmcmedicsupp.com/',
    'PharmaTrust website' => 'https://pharmatrust.tech/',
    'OpteLux shop' => 'https://optelux.com/',
    'AI Employees website' => 'https://phmnai.com/',
];
// Above public_html: the Git deploy deletes anything inside it that is not in the repo.
$stateFile = dirname(__DIR__, 2) . '/mini-ai-watch-state.json';
$first = !is_file($stateFile); // the very first run e-mails once, to prove cron and mail both work
$state = $first ? [] : (json_decode((string) file_get_contents($stateFile), true) ?: []);

function answers($url) {
    $c = curl_init($url);
    curl_setopt_array($c, [CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => true, CURLOPT_MAXREDIRS => 3,
        CURLOPT_TIMEOUT => 25, CURLOPT_CONNECTTIMEOUT => 15, CURLOPT_USERAGENT => 'DrQariaMiniAI-watch/1.0']);
    curl_exec($c);
    $code = (int) curl_getinfo($c, CURLINFO_RESPONSE_CODE);
    curl_close($c);
    return $code >= 200 && $code < 400;
}

$down = [];
$back = [];
$lines = [];
foreach ($checks as $name => $url) {
    $ok = answers($url);
    $s = $state[$name] ?? ['fails' => 0, 'alerted' => false];
    $s['fails'] = $ok ? 0 : $s['fails'] + 1;
    if (!$ok && $s['fails'] >= 2 && !$s['alerted']) { $down[] = $name; $s['alerted'] = true; }
    if ($ok && $s['alerted']) { $back[] = $name; $s['alerted'] = false; }
    $state[$name] = $s;
    $lines[] = ($ok ? 'OK    ' : 'DOWN  ') . $name;
}
file_put_contents($stateFile, json_encode($state));

$test = in_array('--test', $argv ?? [], true);
$marker = dirname(__DIR__, 2) . '/mini-ai-watch-mailtest-2';
if (!is_file($marker)) { touch($marker); $test = true; } // one test after a change of mail settings
if ($down || $back || $test || $first) {
    $subject = $down ? 'Server alert: not answering: ' . implode(', ', $down)
        : ($back ? 'Server alert: back: ' . implode(', ', $back) : 'Mini AI outside watcher: ' . ($first ? 'started' : 'test message'));
    $body = "Dr. Qaria Mini AI outside watcher, checked from outside the main server.\n\n" . implode("\n", $lines)
        . "\n\nIf the main server is down, see the recovery guide in the Claude drive: Dr Qaria Mini AI > 03 Recovery guide.\n";
    $sent = mail($to, $subject, $body, "Content-Type: text/plain; charset=UTF-8\r\n"); // Hostinger's own sender
    echo ($sent ? 'mail handed over: ' : 'MAIL FAILED: ') . $subject . "\n";
}
echo implode("\n", $lines) . "\n";
