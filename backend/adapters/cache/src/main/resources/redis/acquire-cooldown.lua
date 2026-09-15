
if redis.call('SET', KEYS[1], '1', 'NX', 'EX', ARGV[1]) then
    return {1, 0}
end
local remaining = redis.call('PTTL', KEYS[1])
if remaining < 0 then
    remaining = 0
end
return {0, remaining}
