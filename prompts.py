from langchain.prompts import ChatPromptTemplate

schema_definition = """
Fields: variant_id, gene, allele, zygosity, known_effect, confidence, category
"""


select_file_type_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant selecting the correct data format for genetic data (VCF or 23andMe raw data)"),
    ("user",
     "User provided file path: {input_path}. Select the correct data format from the following options: {options}")
])


generate_category_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant generating report for category for a given SNP."),
    ("user", """
    SNP data: {data}
     
    Generate a high visual quality, easy to understand for non-genetic audience, report for all the items in the category.
    
    Output in HTML and Tailwind CSS.
    
    """)
])


# Node: Improve / normalize input instruction (optional)
improve_instruction_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant standardizing user inputs."),
    ("user",
     "User provided file path: {input_path}. Ensure this is a valid path or URL.")
])

# Node: LLM prompt to explain variants
perplexity_search_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a genetic expert assistant."),
    ("user", '''
    
for the following data, generate a comprehensive SNP variant report including:
{data}

Generate a comprehensive SNP variant report including:

Variant Description:
Provide detailed information about the genetic variants, incorporating known data from ClinVar, SNPedia, and gnomAD. Explain the commonalities and differences among these databases, describe the test performed, and clarify the biological or clinical significance of these variants.

Known Effect:
Summarize any established effects or implications of the variants on health, traits, or disease risk, based on current scientific knowledge.

Practical Takeaways:
Highlight actionable insights or recommendations for the user, if applicable, such as lifestyle changes, further testing, or medical consultations.

Confidence Level:
Assess how well-studied these variants are, and express the level of confidence or uncertainty in the current understanding of their effects.


''')
])

report_section_prompt = ChatPromptTemplate.from_messages([
    ("system", " You are a genetics expert LLM. Given information about a genetic variant (such as its ID or description), generate a clear, structured explanation that includes."),
    ("user", """
   
    Based on the SNP data, generate a clear, structured explanation that includes:
    
    Make sure the language is easy to understand and follow for non-genetic audience.
    
    Use common name of the gene instead of rsID. Try to avoid technical terms as much as possible.
    
    Generate a comprehensive SNP variant report by also keeping the user profile in mind, when relevant:

    Variant Description:
    Provide detailed information about the genetic variants, incorporating known data from ClinVar, SNPedia, and gnomAD. Explain the commonalities and differences among these databases, describe the test performed, and clarify the biological or clinical significance of these variants.
   

    Known Effect:
    Summarize any established effects or implications of the variants on health, traits, or disease risk, based on current scientific knowledge for this user profile.

    Practical Takeaways:
    Highlight actionable insights or recommendations for the user, if applicable, such as lifestyle changes, further testing, or medical consultations for this user profile.

    Confidence Level:
    Assess how well-studied these variants are, and express the level of confidence or uncertainty in the current understanding of their effects.

    Citations:
    Pick top relevant scientific articles, databases, or authoritative sources used to compile the information from given citations list.

    Use ** ** to bold important words, and * * to italicize technical words requiring more explanation.
    
    
    Following is the data for a panel of SNP / variants, merge the data and make the report easy to understand and follow for non-genetic audience:
    {data}
    
    User profile, Background information about the user:
    {user_profile}
    
    citations:
    {citations}
    """)
])


ui_example = """

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Genetic Testing Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        
        <!-- Report Summary -->
        <div class="bg-white shadow-md rounded-lg overflow-hidden mb-8">
            <div class="bg-blue-50 px-6 py-4 border-l-4 border-blue-500">
                <h2 class="text-xl font-bold text-gray-800">How Your Body Processes Nutrients and Chemicals</h2>
                <p class="text-gray-600 mt-1">Easy overview of How your genes may affect digestion, energy use, and detox.</p>
            </div>
            
            <div class="p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-3">Variant Description</h3>
                <p class="text-gray-700 mb-4">
                    This report looks at specific spots in your DNA that can influence how your body handles vitamins, breaks down toxins, and uses energy. We compare your results to trusted public resources to help explain what they might mean for you.
                </p>
                
                
            </div>
        </div>
        
        <!-- Detailed Results -->
        <div class="bg-white shadow-md rounded-lg overflow-hidden mb-8">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-xl font-bold text-gray-800">What We Checked</h2>
            </div>
            
            <div class="p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-3">What We Found</h3>
                <div class="bg-gray-50 p-5 rounded-md mb-6">
                    <p class="text-gray-700 mb-4">
                        We looked at changes in your DNA that can affect how your body:
                    </p>
                    <ul class="list-disc pl-5 mb-4 text-gray-700 space-y-1">
                        <li>Uses B vitamins to support energy and cell repair</li>
                        <li>Processes and removes waste compounds safely</li>
                        <li>Handles caffeine and other common substances</li>
                    </ul>
                    
                    <h4 class="text-md font-semibold text-gray-800 mt-5 mb-2">Summary of Your Results:</h4>
                    <ul class="list-disc pl-5 text-gray-700 space-y-1">
                        <li>Vitamin processing: You have a common variation that may need a little extra support with B vitamins.</li>
                        <li>Waste removal: You show typical ability to clear out toxins.</li>
                        <li>Caffeine use: You likely process caffeine faster/slower than average.</li>
                    </ul>
                    
                    <p class="text-gray-700 mt-4">
                        We used several public genetics sites to compare your results: clinical databases for health connections, literature summaries for overall effects, and large population studies for how common these changes are.
                    </p>
                </div>
                
                <!-- Results Table -->
                <h3 class="text-lg font-semibold text-gray-800 mb-3">Your Specific Changes</h3>
                <div class="overflow-x-auto mb-6">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Feature</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Identifier</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Common Label</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Effect</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">B Vitamin Support</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">rs1801131</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">A1298C</td>
                                <td class="px-6 py-4 text-sm text-gray-500">May need extra B vitamins</td>
                            </tr>
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Folate Processing</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">rs1801133</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">C677T</td>
                                <td class="px-6 py-4 text-sm text-gray-500">Affects folate use</td>
                            </tr>
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Vitamin B12 Use</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">rs1801394</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">A66G</td>
                                <td class="px-6 py-4 text-sm text-gray-500">Typical B12 support</td>
                            </tr>
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Detox Helpers</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">rs1695</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">I105V</td>
                                <td class="px-6 py-4 text-sm text-gray-500">Normal detox function</td>
                            </tr>
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Caffeine Response</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">rs762551</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">-</td>
                                <td class="px-6 py-4 text-sm text-gray-500">Process caffeine [fast/slow]</td>
                            </tr>
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Oxidative Stress</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">rs1800566</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">P187S</td>
                                <td class="px-6 py-4 text-sm text-gray-500">Normal stress response</td>
                            </tr>
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Homocysteine Balance</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">rs234706</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">C699T</td>
                                <td class="px-6 py-4 text-sm text-gray-500">Typical balance</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- Known Effects -->
                <h3 class="text-lg font-semibold text-gray-800 mb-3">What This Means for You</h3>
                <div class="bg-gray-50 p-5 rounded-md mb-6">
                    <ul class="list-disc pl-5 text-gray-700 space-y-2">
                        <li>B Vitamin Support: You might benefit from eating extra leafy greens or taking a B-complex vitamin.</li>
                        <li>Folate Processing: Consider foods rich in folate like beans and spinach.</li>
                        <li>Vitamin B12 Use: Your body handles B12 as expected; maintain regular intake.
                        </li>
                        <li>Detox Helpers: A healthy diet and avoiding smoking will support your detox pathways.</li>
                        <li>Caffeine Response: Adjust coffee or tea intake based on how you feel after drinking.
                        </li>
                        <li>Oxidative Stress: No special concerns; antioxidants from fruits and vegetables help keep things balanced.</li>
                        <li>Homocysteine Balance: Regular exercise and B-vitamin rich foods help maintain balance.</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Recommendations -->
        <div class="bg-white shadow-md rounded-lg overflow-hidden mb-8">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-xl font-bold text-gray-800">Personalized Tips</h2>
            </div>
            
            <div class="p-6">
                <div class="bg-green-50 p-5 rounded-md mb-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">Simple Takeaways</h3>
                    <ul class="list-disc pl-5 text-gray-700 space-y-2">
                        <li>Include more B vitamin foods like whole grains, eggs, and leafy greens.</li>
                        <li>Enjoy fruits and vegetables rich in antioxidants daily.</li>
                        <li>Listen to your body after caffeine; adjust intake if you feel jittery.</li>
                        <li>Stay active and hydrated to support natural detox processes.</li>
                        <li>If you have concerns about vitamins or heart health, talk with your doctor about screening options.</li>
                    </ul>
                </div>
                
                <div class="bg-blue-50 p-5 rounded-md">
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">How Confident We Are</h3>
                    <ul class="list-disc	pl-5 text-gray-700 space-y-2">
                        <li>Most findings are well-studied and apply to many people.</li>
                        <li>Small effects may vary based on diet, lifestyle, and other factors.</li>
                        <li>This information complements, but does not replace, medical advice.</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- References -->
        <div class="bg-white shadow-md rounded-lg overflow-hidden">
            <div	class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-xl font-bold text-gray-800">Learn More</h2>
            </div>
            
            <div class="p-6">
                <ul class="list-decimal pl-5 text-gray-700 space-y-2">
                    <li><a href="https://www.webmd.com/a-to-z-guides/mthfr-gene-mutation-tests-symptoms-treatment" class="text-blue-600 hover:underline">WebMD: Information on Vitamin Processing</a></li>
                    <li><a href="https://www.medicalnewstoday.com/articles/326181" class="text-blue-600 hover:underline">Medical News Today: How Your Body Uses B Vitamins</a></li>
                    <li><a href="https://www.healthline.com/nutrition/antioxidants-explained" class="text-blue-600 hover:underline">Healthline: Antioxidants and You</a></li>
                    <li><a href="https://www.cdc.gov/nutrition/data-statistics/" class="text-blue-600 hover:underline">CDC: Nutrition Data and Research</a></li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>

"""

report_ui_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a genetics expert LLM. Given information about a genetic variant (such as its ID or description), generate a clear, structured explanation that includes."),
    ("user", """
     
    Based on Given Genetic Data, generate a report in HTML and Tailwind CSS.

    The report should be easy to understand and follow for non-genetic audience.

    example of the UI styling:

    {ui_example}

    Full report data with mutliple different sections:
    {data}
     
    """)
]).partial(ui_example=ui_example)
