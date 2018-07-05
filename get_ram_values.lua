LUA_PATH = "D:\Work\python\battle_city-neat\socket.lua"

local host, port = "127.0.0.1", 1247
local socket = require("socket")
local tcp = assert(socket.tcp())

tcp:connect(host, port)

-----------------------------------------------
-- RAM addresses.
-----------------------------------------------

-----------------------------------------------
-- Player tank X, Y coordinates.

Tx = 0x90
Ty = 0x98
-----------------------------------------------

-----------------------------------------------
-- Enemy tanks X, Y coordinates.
-- There can only be max 4 enemy tanks
-- at one time.

E1x = 0x92
E2x = 0x93
E3x = 0x94
E4x = 0x95

E1y = 0x9A
E2y = 0x9B
E3y = 0x9C
E4y = 0x9D
-----------------------------------------------

-----------------------------------------------
-- Enemy bullets X, Y coordinates.
-- Each enemy tank can fire one bullet
-- at one time until it hits something.

B1x = 0xBA
B2x = 0xBB
B3x = 0xBC
B4x = 0xBD

B1y = 0xC4
B2y = 0xC5
B3y = 0xC6
B4y = 0xC7
-----------------------------------------------

-----------------------------------------------
-- Misc RAM values:
-- Player lives left.
-- Powerup position.
-- Powerup status.
-- Player tank state.
-- Player shield state.
-- Base status.

Lives = 0x51
Power_pos = 0xC0
Power_stat = 0x49
Tank_state = 0xA8
Shield = 0x89
Eagle = 0x76E

-----------------------------------------------

-----------------------------------------------
-- Score numerals:

Ones = 0x1B
Tens = 0x1A
Hundreds = 0x19
Thousands = 0x18
Tenthousands = 0x17
Hundredthousands = 0x16
Millions = 0x15

-----------------------------------------------

function get_score()
    -- Score numeral concatanation.
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
while (true) do -- outer loop for continuous running
    savestate.load(save)
    local frames = 0
    local eagle_dead = "false"
    while (true) do -- inner loop for each genome

        -- checking if the base is destroyed or no lives left:
        if memory.readbyte(Eagle) ~= 201 or memory.readbyte(Lives) == 0 then do
            local score = get_score()
            if memory.readbyte(Eagle) ~= 201 then do eagle_dead = "true" end end
            tcp:send("end," .. tostring(frames) .. ',' .. score .. ',' .. eagle_dead)
            break
            end
        end

        -- control table with all buttons set to not pressed
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

        -- a loop to get all the RAM values for each brick object.
        -- overall there are 26 * 26 = 676 values
        for adr_first = 0x442, 0x77b, 0x20 do
            local adr_last = adr_first + 0x19
            for adr = adr_first, adr_last do
                table.insert(list, memory.readbyte(adr))
            end
        end

        -- reading all the other RAM values
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

        tcp:send(table.concat(list, ",")) -- concatanating everything into a string and sending it through the socket
                                          -- to the python evaluation script.

        -- now the lua script waits for the receiving message back on what command to do.
        -- the command is then activated by changing the button in the control_table to 'true'
        local command = tcp:receive()
        if command ~= "nothing" and command ~= nil then do control_table[command] = "true" end end
        joypad.set(1, control_table)

        emu.frameadvance() -- advance the emulation by one frame
        frames = frames + 1
    end
end
tcp:close()
