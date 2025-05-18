<template>
    <div class="knowledge-view">
      <div class="knowledge-header">
        <h1>知识库</h1>
        <el-input
          v-model="searchQuery"
          placeholder="搜索知识库..."
          prefix-icon="Search"
          clearable
          class="search-input"
        ></el-input>
      </div>
      
      <div class="knowledge-content">
        <div class="knowledge-categories">
          <div 
            v-for="category in categories" 
            :key="category"
            :class="['category-item', { active: selectedCategory === category }]"
            @click="selectedCategory = category"
          >
            {{ category }}
          </div>
        </div>
        
        <div class="knowledge-items">
          <div 
            v-for="item in filteredItems" 
            :key="item.id"
            class="knowledge-card"
          >
            <h3>{{ item.title }}</h3>
            <div class="knowledge-content">{{ item.content }}</div>
            <div class="knowledge-meta">
              <span class="knowledge-category">{{ item.category }}</span>
            </div>
          </div>
          
          <div v-if="filteredItems.length === 0" class="empty-state">
            <el-icon size="48"><DocumentRemove /></el-icon>
            <p>暂无相关知识条目</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  import { DocumentRemove, Search } from '@element-plus/icons-vue';
  
  // 页面状态
  const searchQuery = ref('');
  const selectedCategory = ref('全部');
  
  // 预设知识库条目
  const knowledgeItems = [
    {
      id: 1,
      title: '蛋白质结构预测概述',
      category: '基础知识',
      content: '蛋白质结构预测是生物信息学中的重要问题，深度学习方法在这一领域取得了显著进展。特别是AlphaFold2等模型的出现，大大提高了预测精度。蛋白质结构预测的目标是根据氨基酸序列预测蛋白质的三维结构，这对于理解蛋白质功能、药物设计和疾病研究具有重要意义。'
    },
    {
      id: 2,
      title: '深度学习在蛋白质结构预测中的应用',
      category: '研究方法',
      content: '深度学习在蛋白质结构预测中的应用主要包括：使用CNN预测接触图谱、使用RNN处理序列信息、应用注意力机制捕捉长程依赖关系等。这些方法极大地提高了预测精度。近年来，深度学习模型在CASP（蛋白质结构预测关键评估）竞赛中表现出色，显著超越了传统方法。'
    },
    {
      id: 3,
      title: 'AlphaFold2技术解析',
      category: '前沿技术',
      content: 'AlphaFold2是DeepMind开发的蛋白质结构预测模型，在CASP14比赛中取得了突破性成果。它使用注意力机制和深度学习方法，能够准确预测蛋白质的三维结构，精度接近实验方法。AlphaFold2的核心创新在于其能够有效整合进化信息和物理约束，通过多头注意力机制捕捉氨基酸之间的长程相互作用。'
    },
    {
      id: 4,
      title: '蛋白质结构预测的应用领域',
      category: '应用',
      content: '蛋白质结构预测的应用包括：药物设计、疾病机理研究、酶工程、疫苗开发等。通过了解蛋白质的三维结构，科学家可以更好地理解其功能并设计针对性的干预方法。在药物开发中，准确的蛋白质结构可以帮助设计更有效的药物分子；在疾病研究中，可以揭示突变如何影响蛋白质结构和功能。'
    },
    {
      id: 5,
      title: '卷积神经网络在蛋白质结构预测中的应用',
      category: '研究方法',
      content: '卷积神经网络(CNN)在蛋白质结构预测中主要用于预测氨基酸残基之间的接触图谱和距离图谱。通过分析多序列比对(MSA)生成的特征，CNN可以识别出远距离氨基酸之间的相互作用模式，这对于预测蛋白质的三维折叠至关重要。'
    },
    {
      id: 6,
      title: '循环神经网络处理蛋白质序列信息',
      category: '研究方法',
      content: '循环神经网络(RNN)特别是LSTM和GRU变体，在处理蛋白质的序列信息方面表现出色。这些模型能够捕捉氨基酸序列中的长程依赖关系，有助于预测蛋白质的二级结构和局部构象特征，为三维结构预测提供重要信息。'
    }
  ];
  
  // 计算所有分类
  const categories = computed(() => {
    const cats = ['全部', ...new Set(knowledgeItems.map(item => item.category))];
    return cats;
  });
  
  // 过滤知识条目
  const filteredItems = computed(() => {
    let items = knowledgeItems;
    
    // 按分类筛选
    if (selectedCategory.value !== '全部') {
      items = items.filter(item => item.category === selectedCategory.value);
    }
    
    // 按搜索关键词筛选
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      items = items.filter(item => 
        item.title.toLowerCase().includes(query) || 
        item.content.toLowerCase().includes(query)
      );
    }
    
    return items;
  });
  </script>
  
  <style scoped>
  .knowledge-view {
    padding: 24px;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  .knowledge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  
  .search-input {
    width: 300px;
  }
  
  .knowledge-content {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  
  .knowledge-categories {
    width: 200px;
    padding-right: 24px;
    border-right: 1px solid #e6e6e6;
    overflow-y: auto;
  }
  
  .category-item {
    padding: 12px 16px;
    cursor: pointer;
    border-radius: 4px;
    margin-bottom: 8px;
    transition: all 0.3s;
  }
  
  .category-item:hover {
    background-color: #f5f7fa;
  }
  
  .category-item.active {
    background-color: #ecf5ff;
    color: #409eff;
  }
  
  .knowledge-items {
    flex: 1;
    padding-left: 24px;
    overflow-y: auto;
  }
  
  .knowledge-card {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  }
  
  .knowledge-card h3 {
    margin-bottom: 12px;
    color: #303133;
  }
  
  .knowledge-content {
    color: #606266;
    line-height: 1.6;
    margin-bottom: 16px;
  }
  
  .knowledge-meta {
    display: flex;
    align-items: center;
  }
  
  .knowledge-category {
    background-color: #ecf5ff;
    color: #409eff;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 300px;
    color: #909399;
  }
  
  .empty-state p {
    margin-top: 16px;
  }
  </style>
  