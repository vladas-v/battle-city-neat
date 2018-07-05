LUA_PATH = "D:\Work\python\battle_city-neat\socket.lua"

local host, port = "127.0.0.1", 1247
local socket = require("socket")
local tcp = assert(socket.tcp())

tcp:connect(host, port)

--tcp:send("hello\n")
--line = tcp:receive()

Tx = 0x90
Ty = 0x98

E1x = 0x92
E2x = 0x93
E3x = 0x94
E4x = 0x95

E1y = 0x9A
E2y = 0x9B
E3y = 0x9C
E4y = 0x9D

B1x = 0xBA
B2x = 0xBB
B3x = 0xBC
B4x = 0xBD

B1y = 0xC4
B2y = 0xC5
B3y = 0xC6
B4y = 0xC7

Lives = 0x51
Power_pos = 0xC0
Power_stat = 0x49
Tank_state = 0xA8
Shield = 0x89
Eagle = 0x76E

--score addr:
Ones = 0x1B
Tens = 0x1A
Hundreds = 0x19
Thousands = 0x18
Tenthousands = 0x17
Hundredthousands = 0x16
Millions = 0x15

function get_score()

    local Ones = memory.readbyte(Ones)
    local Tens = memory.readbyte(Tens)
    local Hundreds = memory.readbyte(Hundreds)
    local Thousands = memory.readbyte(Thousands)
    local Tenthousands = memory.readbyte(Tenthousands)
    local Hundredthousands = memory.readbyte(Hundredthousands)
    local Millions = memory.readbyte(Millions)
    local score = Millions .. Hundredthousands .. Tenthousands .. Thousands .. Hundreds .. Tens .. Ones

    return score
end

emu.speedmode("maximum")
save = savestate.object('10')
while (true) do
    savestate.load(save)
    local frames = 0
    local eagle_dead = "false"
    while (true) do
        --local t = os.clock()
        if memory.readbyte(Eagle) ~= 201 or memory.readbyte(Lives) == 0 then do
            local score = get_score()
            if memory.readbyte(Eagle) ~= 201 then do eagle_dead = "true" end end
            tcp:send("end," .. tostring(frames) .. ',' .. score .. ',' .. eagle_dead)
            break
            end
        end
        local control_table = {
            A=false,
            up=false,
            left=false,
            B=false,
            select=false,
            right=false,
            down=false,
            start=false
        }
        local list = {}
        for adr_first = 0x442, 0x77b, 0x20 do
            local adr_last = adr_first + 0x19
            for adr = adr_first, adr_last do
                table.insert(list, memory.readbyte(adr))
            end
        end

        table.insert(list, memory.readbyte(Tx))
        table.insert(list, memory.readbyte(Ty))

        table.insert(list, memory.readbyte(E1x))
        table.insert(list, memory.readbyte(E2x))
        table.insert(list, memory.readbyte(E3x))
        table.insert(list, memory.readbyte(E4x))

        table.insert(list, memory.readbyte(E1y))
        table.insert(list, memory.readbyte(E2y))
        table.insert(list, memory.readbyte(E3y))
        table.insert(list, memory.readbyte(E4y))

        table.insert(list, memory.readbyte(B1x))
        table.insert(list, memory.readbyte(B2x))
        table.insert(list, memory.readbyte(B3x))
        table.insert(list, memory.readbyte(B4x))

        table.insert(list, memory.readbyte(B1y))
        table.insert(list, memory.readbyte(B2y))
        table.insert(list, memory.readbyte(B3y))
        table.insert(list, memory.readbyte(B4y))

        table.insert(list, memory.readbyte(Lives))
        table.insert(list, memory.readbyte(Power_pos))
        table.insert(list, memory.readbyte(Power_stat))
        table.insert(list, memory.readbyte(Tank_state))
        table.insert(list, memory.readbyte(Shield))

        tcp:send(table.concat(list, ","))
        --tcp:close()
        --os.exit()
        local command = tcp:receive()
        if command ~= "nothing" and command ~= nil then do control_table[command] = "true" end end
        joypad.set(1, control_table)
        emu.frameadvance()
        frames = frames + 1
        --print(string.format("elapsed time: %.2f\n", os.clock() - t))
    end
end
tcp:close()
