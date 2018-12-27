import org.junit.jupiter.api.Test;

import java.util.*;

public class DarwinTest {

    @Test
    public void testRepetition() {
        String darwin1859_1 = "WHEN we look to the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
        String darwin1860_1 = "WHEN we look to the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
        String darwin1861_1 = "WHEN we look to the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
        String darwin1866_1 = "Causes of Variability. WHEN we look to the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
        String darwin1869_1 = "Causes of Variability. WHEN we compare the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
        String darwin1872_1 = "Causes of Variability. WHEN we compare the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";


        // We need to tokenize the witnesses
        List<String> tokens1 = tokenize(darwin1859_1);
        List<String> tokens2 = tokenize(darwin1866_1);
        Map<String, List<String>> witnessData = new HashMap<>();
        witnessData.put("darwin1859", tokens1);
        witnessData.put("darwin1866", tokens2);


        Map<List<String>, List<Collate.Skipgram>> commonSequenceTable = Collate.createCommonSequenceTable(witnessData);

        // We create a function that calculates the uniqueness of each key in the common sequence table
        Map<List<String>, Collate.AnalyticResult> uniquenessFactor = Collate.analyse(commonSequenceTable);


        // the reasoning during the creation of the priority list is too simple
        // we first need to gather more info to be able to able to make better decisions.
        List<List<String>> commonSequencePriorityList = Collate.createCommonSequencePriorityList(commonSequenceTable);

        // Diagnostic output
        for (List<String> key : commonSequencePriorityList) {
            System.out.println(String.join(" ", key) + " " + uniquenessFactor.get(key)+" "+commonSequenceTable.get(key));
        }

        // we create the topological ordered list
        // by selecting one skip bigram from the common sequence priority list
        List<VariantGraphCreator.Node> topologicalList = VariantGraphCreator.initList();


        for (List<String> normalizedBigram : commonSequencePriorityList) {
           // get the actual bigrams from the CST
            List<Collate.Skipgram> skipgrams = commonSequenceTable.get(normalizedBigram);

            for(Collate.Skipgram skipgram : skipgrams) {
                selectSkipgram(skipgram, witnessData, topologicalList);
            }
        }

        System.out.println(topologicalList);


    }

    private void selectSkipgram(Collate.Skipgram skipgram, Map<String, List<String>> witnessData, List<VariantGraphCreator.Node> topologicalList) {
        // we must look for the location where to insert the vertex
        // we have to get the tokens out of the bigram
        // this method has to be called twice. Once for each token in the skipgram
        String witnessId = skipgram.witnessId;
        int position = skipgram.first;
        String value = witnessData.get(witnessId).get(position);
        VariantGraphCreator.insertTokenInVariantGraph(topologicalList, witnessId, position, value);

        position = skipgram.second;
        value = witnessData.get(witnessId).get(position);
        VariantGraphCreator.insertTokenInVariantGraph(topologicalList, witnessId, position, value);
    }


    // We split on whitespace for now
    // This could be improved later.
    private List<String> tokenize(String content) {
        String[] strings = content.split(" ");
        return Arrays.asList(strings);
    }
}
