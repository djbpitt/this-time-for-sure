import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DarwinTest {

    @Test
    public void testRepetition() throws IOException {
//        String darwin1859_1 = "WHEN we look to the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
//        String darwin1860_1 = "WHEN we look to the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
//        String darwin1861_1 = "WHEN we look to the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
//        String darwin1866_1 = "Causes of Variability. WHEN we look to the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
//        String darwin1869_1 = "Causes of Variability. WHEN we compare the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";
//        String darwin1872_1 = "Causes of Variability. WHEN we compare the individuals of the same variety or sub-variety of our older cultivated plants and animals, one of";

        System.out.println("Working Directory = " +
                System.getProperty("user.dir"));

        // read darwin 1859 file
        String darwin1859_1 = Collate.readTextFile("../darwin/chapter_1_paragraph_1/darwin1859_par1.txt");
        String darwin1866_1 = Collate.readTextFile("../darwin/chapter_1_paragraph_1/darwin1866_par1.txt");





        // We need to tokenize the witnesses
        List<String> tokens1 = tokenize(darwin1859_1);
        List<String> tokens2 = tokenize(darwin1866_1);
        Map<String, List<String>> witnessData = new HashMap<>();
        witnessData.put("darwin1859", tokens1);
        witnessData.put("darwin1866", tokens2);

        Collate.collate(witnessData);



    }



    // We split on whitespace for now
    // This could be improved later.
    private List<String> tokenize(String content) {
        String[] strings = content.split(" ");
        return Arrays.asList(strings);
    }
}
