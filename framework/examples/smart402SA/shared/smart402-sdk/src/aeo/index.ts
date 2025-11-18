/**
 * Smart402 AEO (Answer Engine Optimization) Engine
 * Optimizes contracts for AI discoverability and semantic understanding
 */

import type {
  AEOConfig,
  AEOResult,
  Recommendation,
  AEOMetadata,
  Smart402Config,
  UCLLayer
} from '../types/index.js';

export class AEOEngine {
  private config: Required<AEOConfig>;
  private readonly version = '1.0.0';

  constructor(config: AEOConfig = {}) {
    this.config = {
      target_score: config.target_score ?? 0.85,
      optimize_for: config.optimize_for ?? ['clarity', 'completeness', 'discoverability'],
      schema_org: config.schema_org ?? true,
      keywords: config.keywords ?? []
    };
  }

  /**
   * Calculate AEO score for a Smart402 contract
   */
  async calculateScore(contractConfig: Smart402Config, ucl?: UCLLayer): Promise<AEOResult> {
    const startTime = Date.now();
    const factors: Record<string, number> = {};

    // Factor 1: Content Clarity (0-0.25)
    factors.clarity = this.evaluateClarity(contractConfig);

    // Factor 2: Structural Completeness (0-0.25)
    factors.completeness = this.evaluateCompleteness(contractConfig, ucl);

    // Factor 3: Semantic Richness (0-0.20)
    factors.semantic_richness = this.evaluateSemanticRichness(contractConfig);

    // Factor 4: Discoverability (0-0.20)
    factors.discoverability = this.evaluateDiscoverability(contractConfig);

    // Factor 5: Schema.org Compliance (0-0.10)
    factors.schema_compliance = this.config.schema_org ?
      this.evaluateSchemaCompliance(contractConfig) : 0;

    // Calculate total score
    const score = Object.values(factors).reduce((sum, val) => sum + val, 0);

    // Generate recommendations
    const recommendations = this.generateRecommendations(factors, contractConfig);

    // Generate Schema.org metadata if enabled
    const schema_org = this.config.schema_org ?
      this.generateSchemaOrg(contractConfig) : undefined;

    const metadata: AEOMetadata = {
      timestamp: new Date(),
      version: this.version,
      analysis_time_ms: Date.now() - startTime,
      factors
    };

    return {
      score: Math.min(score, 1.0),
      recommendations,
      metadata,
      schema_org
    };
  }

  /**
   * Optimize contract configuration for better AEO score
   */
  async optimize(contractConfig: Smart402Config): Promise<Smart402Config> {
    const optimized = { ...contractConfig };

    // Enhance description with keywords
    if (this.config.keywords.length > 0) {
      optimized.metadata = {
        ...optimized.metadata,
        keywords: [...(optimized.metadata?.keywords ?? []), ...this.config.keywords],
        optimized_for_aeo: true,
        aeo_version: this.version
      };
    }

    // Add structured metadata
    if (!optimized.metadata?.schemaOrg && this.config.schema_org) {
      optimized.metadata = {
        ...optimized.metadata,
        schemaOrg: this.generateSchemaOrg(contractConfig)
      };
    }

    // Ensure clear party definitions
    if (optimized.parties) {
      optimized.parties = optimized.parties.map(party => ({
        ...party,
        metadata: {
          ...party.metadata,
          role_description: party.role,
          semantic_type: this.inferPartyType(party.role)
        }
      }));
    }

    return optimized;
  }

  /**
   * Evaluate content clarity (max 0.25)
   */
  private evaluateClarity(config: Smart402Config): number {
    let score = 0;

    // Clear title (0.05)
    if (config.title && config.title.length >= 10 && config.title.length <= 100) {
      score += 0.05;
    }

    // Comprehensive description (0.10)
    if (config.description) {
      const wordCount = config.description.split(/\s+/).length;
      if (wordCount >= 20 && wordCount <= 500) {
        score += 0.10;
      } else if (wordCount >= 10) {
        score += 0.05;
      }
    }

    // Clear party roles (0.05)
    if (config.parties && config.parties.length > 0) {
      const hasRoles = config.parties.every(p => p.role && p.role.length > 0);
      if (hasRoles) score += 0.05;
    }

    // Well-structured terms (0.05)
    if (config.terms && typeof config.terms === 'object') {
      const termCount = Object.keys(config.terms).length;
      if (termCount >= 3) score += 0.05;
    }

    return Math.min(score, 0.25);
  }

  /**
   * Evaluate structural completeness (max 0.25)
   */
  private evaluateCompleteness(config: Smart402Config, ucl?: UCLLayer): number {
    let score = 0;

    // Has all required fields (0.10)
    const requiredFields = ['type', 'title', 'description', 'parties'];
    const hasAllRequired = requiredFields.every(field =>
      config[field as keyof Smart402Config]
    );
    if (hasAllRequired) score += 0.10;

    // UCL layer completeness (0.15)
    if (ucl) {
      let layerScore = 0;
      if (ucl.human_readable) layerScore += 0.04;
      if (ucl.llm_structured) layerScore += 0.04;
      if (ucl.machine_executable) layerScore += 0.04;
      if (ucl.blockchain_compilable) layerScore += 0.03;
      score += layerScore;
    }

    return Math.min(score, 0.25);
  }

  /**
   * Evaluate semantic richness (max 0.20)
   */
  private evaluateSemanticRichness(config: Smart402Config): number {
    let score = 0;

    // Keyword richness (0.08)
    const keywords = config.metadata?.keywords ?? [];
    if (keywords.length >= 5) score += 0.08;
    else if (keywords.length >= 3) score += 0.05;
    else if (keywords.length >= 1) score += 0.02;

    // Metadata richness (0.07)
    const metadataFields = config.metadata ? Object.keys(config.metadata).length : 0;
    if (metadataFields >= 5) score += 0.07;
    else if (metadataFields >= 3) score += 0.04;
    else if (metadataFields >= 1) score += 0.02;

    // Contract type specificity (0.05)
    if (config.type && config.type.includes(':')) {
      score += 0.05; // Namespaced type is more specific
    } else if (config.type) {
      score += 0.03;
    }

    return Math.min(score, 0.20);
  }

  /**
   * Evaluate discoverability (max 0.20)
   */
  private evaluateDiscoverability(config: Smart402Config): number {
    let score = 0;

    // Contract ID present (0.05)
    if (config.metadata?.contract_id) {
      score += 0.05;
    }

    // Tags for categorization (0.08)
    const tags = config.metadata?.tags ?? [];
    if (tags.length >= 3) score += 0.08;
    else if (tags.length >= 1) score += 0.04;

    // Searchable terms (0.07)
    const searchableText = [
      config.title,
      config.description,
      ...(config.metadata?.keywords ?? [])
    ].join(' ').toLowerCase();

    const hasBusinessTerms = /\b(service|payment|contract|agreement|transaction)\b/.test(searchableText);
    if (hasBusinessTerms) score += 0.07;

    return Math.min(score, 0.20);
  }

  /**
   * Evaluate Schema.org compliance (max 0.10)
   */
  private evaluateSchemaCompliance(config: Smart402Config): number {
    if (!config.metadata?.schemaOrg) return 0;

    const schema = config.metadata.schemaOrg;
    let score = 0;

    // Has @context and @type (0.05)
    if (schema['@context'] && schema['@type']) {
      score += 0.05;
    }

    // Has required Schema.org fields (0.05)
    const hasRequiredFields = schema.name && schema.description;
    if (hasRequiredFields) score += 0.05;

    return Math.min(score, 0.10);
  }

  /**
   * Generate recommendations for improvement
   */
  private generateRecommendations(
    factors: Record<string, number>,
    config: Smart402Config
  ): Recommendation[] {
    const recommendations: Recommendation[] = [];

    // Clarity recommendations
    if (factors.clarity < 0.20) {
      if (!config.description || config.description.split(/\s+/).length < 20) {
        recommendations.push({
          category: 'clarity',
          priority: 'high',
          message: 'Add a more detailed description (20-500 words) to improve clarity',
          fix: 'Expand the description field with comprehensive contract details'
        });
      }
    }

    // Completeness recommendations
    if (factors.completeness < 0.20) {
      recommendations.push({
        category: 'completeness',
        priority: 'high',
        message: 'Ensure all UCL layers are properly defined',
        fix: 'Complete human_readable, llm_structured, machine_executable, and blockchain_compilable layers'
      });
    }

    // Semantic richness recommendations
    if (factors.semantic_richness < 0.15) {
      const keywords = config.metadata?.keywords ?? [];
      if (keywords.length < 5) {
        recommendations.push({
          category: 'semantic',
          priority: 'medium',
          message: `Add more keywords (current: ${keywords.length}, recommended: 5+)`,
          fix: 'Include relevant industry terms, contract types, and domain-specific keywords'
        });
      }
    }

    // Discoverability recommendations
    if (factors.discoverability < 0.15) {
      recommendations.push({
        category: 'discoverability',
        priority: 'medium',
        message: 'Enhance discoverability with tags and categorization',
        fix: 'Add tags, categories, and searchable metadata fields'
      });
    }

    // Schema.org recommendations
    if (this.config.schema_org && factors.schema_compliance < 0.08) {
      recommendations.push({
        category: 'schema',
        priority: 'low',
        message: 'Add Schema.org structured data for better semantic understanding',
        fix: 'Include @context, @type, name, and description in schemaOrg metadata'
      });
    }

    return recommendations;
  }

  /**
   * Generate Schema.org structured data
   */
  private generateSchemaOrg(config: Smart402Config): any {
    return {
      '@context': 'https://schema.org',
      '@type': 'DigitalDocument',
      name: config.title,
      description: config.description,
      dateCreated: new Date().toISOString(),
      creator: config.parties?.[0] ? {
        '@type': 'Person',
        name: config.parties[0].role,
        identifier: config.parties[0].id
      } : undefined,
      keywords: config.metadata?.keywords?.join(', '),
      inLanguage: 'en',
      encodingFormat: 'application/json',
      additionalType: config.type,
      identifier: config.metadata?.contract_id
    };
  }

  /**
   * Infer semantic party type from role
   */
  private inferPartyType(role: string): string {
    const roleLower = role.toLowerCase();

    if (roleLower.includes('buyer') || roleLower.includes('customer')) return 'Buyer';
    if (roleLower.includes('seller') || roleLower.includes('vendor')) return 'Seller';
    if (roleLower.includes('service')) return 'ServiceProvider';
    if (roleLower.includes('agent') || roleLower.includes('intermediary')) return 'Agent';
    if (roleLower.includes('arbiter') || roleLower.includes('mediator')) return 'Arbiter';

    return 'Participant';
  }
}

export default AEOEngine;
