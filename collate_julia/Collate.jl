#=
Collate:
- Julia version: 1.0.3
- Author: rhdekker
- Date: 2018-12-28
=#


using DataStructures

# create witness data
# TODO: Make ordered dict!

witnessData = Dict( "wit1" => ["a", "b", "c", "d", "e"],
                    "wit2" => ["a", "e", "c","d"],
                    "wit3" => ["a", "d", "b"])

println(typeof(witnessData))
println(witnessData)

csTable = DefaultDict{Tuple, Vector{Tuple{String, Int64, Int64}}}(Vector{Tuple})

for (key, value) in witnessData
    println(key)
#    println(value[1:end])
    for idx in 1:length(value)
        # println("idx1 ", idx)
        for idx2 in idx+1:length(value)
            # println("idx2 ", idx2 )
            push!(csTable[(value[idx], value[idx2])], (key, idx, idx2))
        end
    end
end


    ###
    # Sort table into common sequence list (csList)
    ###
    #   order by 1) number of witnesses (numerical high to low) and 2) sequence (alphabetic low to high)
    println(typeof(collect(keys(csTable))))

#     csList = SortedDict(csTable)

   csList = sort(collect(keys(csTable)))

    # , lt= (x,y) -> y > x DIT IS HETZELFDE ALS DE DEFAULT!
    #, by=k -> (-length(k[2], k[1]))

for item in csList
    println(item,":",csTable[item])
end

