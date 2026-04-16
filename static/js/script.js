let radarChart = null;
let activeSlot = null;
let selectedPokemon = [null, null]; // [Pokemon1, Pokemon2]

const STAT_LIMITS = {
    hp: 255,
    atk: 190,
    def: 250,
    spAtk: 194,
    spDef: 250,
    spd: 200,
    total: 1000
};

document.addEventListener('DOMContentLoaded', function() {
    initChart();
    setupSearch();
});

function initChart() {
    const canvas = document.getElementById('radarChart');
    
    // 1. SEGURANÇA: Destrói o gráfico anterior se ele existir (Evita o bug de sumir/piscar)
    if (radarChart) {
        radarChart.destroy();
    }
    // Verificação extra caso o Chart.js tenha perdido a referência
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
        existingChart.destroy();
    }

    const ctx = canvas.getContext('2d');
    

    const colorP1 = { main: 'rgba(0, 255, 255, 1)', fill: 'rgba(255, 255, 255, 0.01)', point: 'rgba(141, 253, 253, 1)' };
    const colorP2 = { main: 'rgba(255, 0, 200, 1)', fill: 'rgba(100, 100, 100, 0.01)', point: 'rgba(252, 80, 214, 1)' };

    const data = {
        labels: ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed'],
        datasets: [{
            label: 'Pokemon 1',
            data: [], // Inicia zerado para garantir o desenho do grid
            fill: true,
            tension: 0.1,
            borderJoinStyle: 'round',
            borderCapStyle: 'round',
            backgroundColor: colorP1.fill,
            borderColor: colorP1.main,
            pointBackgroundColor: colorP1.point,
            pointBorderColor: colorP1.point,
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: '#fff'
        }, {
            label: 'Pokemon 2',
            data: [],
            fill: true,
            tension: 0.1,
            borderJoinStyle: 'round',
            borderCapStyle: 'round',
            backgroundColor: colorP2.fill,
            borderColor: colorP2.main,
            pointBackgroundColor: colorP2.point,
            pointBorderColor: colorP2.point,
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: '#fff'
        }]
    };

    const config = {
        type: 'radar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            elements: { line: { borderWidth: 3 } },
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.2)' },
                    grid: { color: '#ffffff04' },
                    pointLabels: {
                        color: '#E4EAF4',
                        font: {
                            family: "'Barlow Condensed', sans-serif",
                            size: 16, 
                            weight: '600'
                        },
                        padding: 8
                    },
                    ticks: { display: false, stepSize: 160 },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    backgroundColor: 'rgba(33, 35, 60, 0.2)'
                }
            },
            plugins: { legend: { display: false } },
        }
    };

    // 2. CRIAÇÃO
    radarChart = new Chart(ctx, config);

    // 3. FIX DE RENDERIZAÇÃO
    // Força o navegador a recalcular o tamanho após 100ms
    setTimeout(() => {
        radarChart.resize();
        radarChart.update();
    }, 100);
}

function openSearch(slot) {
    activeSlot = slot;
    const palette = document.getElementById('search-palette');
    const input = document.getElementById('pokemon-search-input');
    
    palette.style.display = 'flex';
    
    input.value = ''; // Limpa o texto
    input.focus();    // Foca
    
    // Zera os resultados anteriores visualmente
    document.getElementById('search-results').innerHTML = '';
}

function closeSearch() {
    document.getElementById('search-palette').style.display = 'none';
    activeSlot = null;
}

function setupSearch() {
    const palette = document.getElementById('search-palette');

    // Removemos o listener de 'input' daqui, o HTMX cuida disso!

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeSearch();
    });

    palette.addEventListener('click', (e) => {
        if (e.target === palette) closeSearch();
    });
}

window.selectPokemon = async function(id) {
    const currentSlot = activeSlot;
    closeSearch();

    if (!currentSlot) return;

    try {
        const response = await fetch(`/api/pokemon/${id}/`);
        if (!response.ok) throw new Error('Erro na API');
        
        const pokemonData = await response.json();

        // Salva no array global
        selectedPokemon[currentSlot - 1] = pokemonData;

        // 1. Atualiza a Tela (Imagem, Nome, Barras e NÚMEROS da tabela)
        // (Certifique-se de estar usando a versão do updateSlotUI que mandei na mensagem anterior)
        updateSlotUI(currentSlot, pokemonData); 
        
        // 2. Atualiza o Gráfico (com a correção acima)
        updateChart();      
        
        // 3. ❌ REMOVA ESTA LINHA:
        // updateStatsTable();  <-- ISSO CAUSA O BUG DOS NÚMEROS SUMINDO

    } catch (error) {
        console.error('Erro:', error);
    }
}

function updateSlotUI(slot, pokemon) {
    const card = document.getElementById(`slot-${slot}`);
    card.classList.remove('empty');
    
    // 1. Dados Básicos
    card.querySelector('.pokemon-name').textContent = pokemon.name;
    card.querySelector('.pokemon-id').textContent = `ID #${pokemon.id.toString().padStart(3, '0')}`;
    
    const img = card.querySelector('.sprite-img');
    img.src = pokemon.sprite; 
    img.style.display = 'block';

    // 2. Tipos
    const typesContainer = card.querySelector('.pokemon-type');
    typesContainer.innerHTML = '';
    typesContainer.classList.add('pokemon-types-container');

    pokemon.types.forEach(type => {
        const span = document.createElement('span');
        span.textContent = type;
        span.className = `type-badge type-${type.toLowerCase()}`;
        typesContainer.appendChild(span);
    });

    // 3. Botão
    const btn = card.querySelector('.add-btn');
    btn.innerHTML = `<i class="ph-bold ph-arrows-counter-clockwise"></i>Change`;

    // 4. Peso e Altura
    const heightEl = document.getElementById(`val-height-${slot}`);
    const weightEl = document.getElementById(`val-weight-${slot}`);
    if (heightEl) heightEl.textContent = (pokemon.height / 10).toFixed(1) + 'm';
    if (weightEl) weightEl.textContent = (pokemon.weight / 10).toFixed(1) + 'kg';

    // 5. STATS (Aqui está a mágica!)
    // Mapeia o nome da API (Django) para o nome que sua função atualizarBarra espera
    const statsMap = {
        'hp': 'hp',
        'attack': 'atk',
        'defense': 'def',
        'special-attack': 'spAtk',
        'special-defense': 'spDef',
        'speed': 'spd',
        'total': 'total'
    };

    for (const [apiKey, htmlSuffix] of Object.entries(statsMap)) {
        const val = pokemon.stats[apiKey]; 

        // Atualiza o Número na tela
        const textEl = document.getElementById(`val-${htmlSuffix}-${slot}`);
        if (textEl) textEl.textContent = val;
        
        // CHAMA SUA FUNÇÃO DE BARRAS AQUI!
        // Passamos o ID da barra, o valor e o tipo (ex: 'spAtk')
        atualizarBarra(`bar-${htmlSuffix}-${slot}`, val, htmlSuffix);
    }
}


function updateChart() {
    // Se o gráfico ainda não foi criado, sai da função (evita erro)
    if (!radarChart) return;

    selectedPokemon.forEach((pokemon, index) => {
        if (pokemon) {
            // AQUI ESTAVA O PROBLEMA: Mapeando para as chaves da API do Django
            const stats = [
                pokemon.stats['hp'],
                pokemon.stats['attack'],          // Antes era .atk
                pokemon.stats['defense'],         // Antes era .def
                pokemon.stats['special-attack'],  // Antes era .spAtk
                pokemon.stats['special-defense'], // Antes era .spDef
                pokemon.stats['speed']            // Antes era .spd
            ];
            
            radarChart.data.datasets[index].data = stats;
            radarChart.data.datasets[index].label = pokemon.name;
        }
    });
    
    radarChart.update();
}

function getPowerColor(total) {
    if (total >= 670) return '#C171FF'; // LENDA
    if (total >= 500) return '#FFDD6E'; // GREAT
    return 'rgba(42, 214, 133, 1)'; // Early game
}

function atualizarBarra(elementoId, valorAtual, tipoStat) {
    const barra = document.getElementById(elementoId);
    if (!barra) return;

    const maximo = STAT_LIMITS[tipoStat]; 
    let porcentagem = (valorAtual / maximo) * 100;
    if (porcentagem > 100) porcentagem = 100;

    if (tipoStat === 'total') {
        const corTier = getPowerColor(valorAtual);
        barra.style.backgroundColor = corTier;
        
    } else {
        // Reset to default for other stats if needed
        barra.style.backgroundColor = 'rgba(42, 214, 133, 1)';
        barra.style.boxShadow = 'none';
    }

    setTimeout(() => {
        barra.style.width = `${porcentagem}%`;
    }, 50);
}
