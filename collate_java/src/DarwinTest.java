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
        Map<List<String>, Float> uniquenessFactor = Collate.analyse(commonSequenceTable);


        // the reasoning during the creation of the priority list is too simple
        // we first need to gather more info to be able to able to make better decisions.
        List<List<String>> commonSequencePriorityList = Collate.createCommonSequencePriorityList(commonSequenceTable);

        // Diagnostic output
        for (List<String> key : commonSequencePriorityList) {
            System.out.println(String.join(" ", key) + " " + commonSequenceTable.get(key));
        }

    }

    // We split on whitespace for now
    // This could be improved later.
    private List<String> tokenize(String content) {
        String[] strings = content.split(" ");
        return Arrays.asList(strings);
    }
}
